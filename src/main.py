import random
import time

import supervisely as sly

import functions as f
import globals as g
import init_ui



@g.my_app.callback("preview")
@sly.timeit
def preview(api: sly.Api, task_id, context, state, app_logger):
    api.task.set_fields(task_id, [{"field": "data.previewProgress", "payload": 0}])

    image_id = random.choice(g.image_ids)
    image_info = api.image.get_info_by_id(image_id)
    image_name = image_info.name

    img = api.image.download_np(image_info.id)
    ann_json = api.annotation.download(image_id).annotation
    ann = sly.Annotation.from_json(ann_json, g.project_meta)

    selected_classes = f.get_selected_classes_from_ui(state["classesSelected"])
    single_crop = f.crop_and_resize_objects(
        [img], [ann], state, selected_classes, [image_name]
    )
    single_crop = f.unpack_single_crop(single_crop, image_name)
    single_crop = [(img, ann)] + single_crop

    grid_data = {}
    grid_layout = [[] for _ in range(g.CNT_GRID_COLUMNS)]

    upload_results = f.upload_preview(single_crop)
    for idx, info in enumerate(upload_results):
        if idx > 8:
            break

        if idx == 0:
            grid_data[idx] = {
                "url": info.storage_path,
                "title": f"Original image ({image_name})",
                "figures": [label.to_json() for label in single_crop[idx][1].labels],
            }
        else:
            grid_data[idx] = {
                "url": info.storage_path,
                "title": f"Object_{idx}",
                "figures": [label.to_json() for label in single_crop[idx][1].labels],
            }
        grid_layout[idx % g.CNT_GRID_COLUMNS].append(idx)

    if grid_data:
        content = {
            "projectMeta": g.project_meta_json,
            "annotations": grid_data,
            "layout": grid_layout,
        }
        api.task.set_fields(
            task_id, [{"field": "data.preview.content", "payload": content}]
        )

    # print(f'{psutil.virtual_memory().percent=}')

def download_images_with_retry(api, dataset_id, image_ids):
    retry_cnt = 5
    curr_retry = 0
    while curr_retry <= retry_cnt:
        try:
            image_nps = api.image.download_nps(dataset_id, image_ids)
            if len(image_nps) != len(image_ids):
                raise RuntimeError(f"Downloaded {len(image_nps)} images, but {len(image_ids)} expected.")
            return image_nps
        except Exception as e:
            curr_retry += 1
            if curr_retry <= retry_cnt:
                time.sleep(1)
                sly.logger.warn(f"Failed to download images, retry {curr_retry} of {retry_cnt}... Error: {e}")
    raise RuntimeError(f"Failed to download images with ids {image_ids}. Check your data and try again. Error: {e}")

@g.my_app.callback("crop_all_objects")
@sly.timeit
def crop_all_objects(api: sly.Api, task_id, context, state, app_logger):
    api.task.set_field(task_id, "data.started", True)
    dst_project = api.project.create(
        g.WORKSPACE_ID,
        state["resultProjectName"],
        type=sly.ProjectType.IMAGES,
        change_name_if_conflict=True,
    )
    if state["keepAnns"] or state["copyTags"]:
        api.project.update_meta(dst_project.id, g.project_meta.to_json())

    progress = sly.Progress("Cropping objects on images", g.total_images_count)
    current_progress = 0
    datasets = api.dataset.get_list(g.PROJECT_ID)
    for dataset in datasets:
        dst_dataset = api.dataset.create(dst_project.id, dataset.name)
        images_infos = api.image.get_list(dataset.id)
        for batch in sly.batched(images_infos):
            image_ids = [image_info.id for image_info in batch]
            image_names = [image_info.name for image_info in batch]
            ann_infos = api.annotation.download_batch(dataset.id, image_ids)

            image_nps = download_images_with_retry(api, dataset.id, image_ids)
            anns = [
                sly.Annotation.from_json(ann_info.annotation, g.project_meta)
                for ann_info in ann_infos
            ]
            selected_classes = f.get_selected_classes_from_ui(state["classesSelected"])
            crops = f.crop_and_resize_objects(
                image_nps, anns, state, selected_classes, image_names
            )
            crop_nps, crop_anns, crop_names = f.unpack_crops(crops, image_names)

            dst_image_infos = api.image.upload_nps(dst_dataset.id, crop_names, crop_nps)
            dst_image_ids = [dst_image_info.id for dst_image_info in dst_image_infos]
            if state["keepAnns"] and state["copyTags"] is False:
                api.annotation.upload_anns(dst_image_ids, crop_anns)
            if state["copyTags"]:
                g.project_meta, need_update = f.validate_tags(g.project_meta)
                if need_update:
                    api.project.update_meta(dst_project.id, g.project_meta.to_json())
                crop_anns = f.copy_tags(crop_anns, state["keepAnns"])
                api.annotation.upload_anns(dst_image_ids, crop_anns)
            progress.iters_done_report(len(batch))
            current_progress += len(batch)
            api.task.set_field(
                task_id,
                "data.progress",
                int(current_progress * 100 / g.total_images_count),
            )

            # print(f'{psutil.virtual_memory().percent=}')

    res_project = api.project.get_info_by_id(dst_project.id)
    fields = [
        {"field": "data.resultProject", "payload": res_project.name},
        {"field": "data.resultProjectId", "payload": res_project.id},
        {
            "field": "data.resultProjectPreviewUrl",
            "payload": api.image.preview_url(res_project.reference_image_url, 100, 100),
        },
        {"field": "data.finished", "payload": True},
    ]
    api.task.set_fields(task_id, fields)
    api.task.set_output_project(task_id, res_project.id, res_project.name)
    g.my_app.stop()


def main():
    data = {}
    state = {}

    init_ui.validate_input_meta(g.project_meta)
    init_ui.init(data, state)

    # initial_events = [
    #     {
    #         "state": state,
    #         "context": None,
    #         "command": "preview"
    #     }
    # ]

    # Run application service
    g.my_app.run(data=data, state=state)


if __name__ == "__main__":
    sly.main_wrapper("main", main)
