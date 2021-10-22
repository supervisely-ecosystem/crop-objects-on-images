import os
import random
import init_ui
import globals as g
import functions as f
import supervisely_lib as sly


@g.my_app.callback("preview")
@sly.timeit
def preview(api: sly.Api, task_id, context, state, app_logger):
    api.task.set_fields(task_id, [{"field": "data.previewProgress", "payload": 0}])

    image_id = random.choice(g.image_ids)
    image_info = api.image.get_info_by_id(image_id)

    img = api.image.download_np(image_info.id)
    ann_json = api.annotation.download(image_id).annotation
    ann = sly.Annotation.from_json(ann_json, g.project_meta)

    crops = f.crop_and_resize_objects([img], [ann], state)
    crops = [(img, ann)] + crops

    grid_data = {}
    grid_layout = [[] for i in range(g.CNT_GRID_COLUMNS)]

    upload_results = f.upload_augs(crops)
    for idx, info in enumerate(upload_results):
        grid_data[info.name] = {"url": info.full_storage_url,
                                "figures": [label.to_json() for label in crops[idx][1].labels]}
        grid_layout[idx % g.CNT_GRID_COLUMNS].append(info.name)

    if len(grid_data) > 0:
        content = {
            "projectMeta": g.project_meta_json,
            "annotations": grid_data,
            "layout": grid_layout
        }
        api.task.set_fields(task_id, [{"field": "data.preview.content", "payload": content}])


@g.my_app.callback("crop_all_objects")
@sly.timeit
def crop_all_objects(api: sly.Api, task_id, context, state, app_logger):
    dst_project = api.project.create(g.WORKSPACE_ID, state["resultProjectName"], type=sly.ProjectType.IMAGES,
                                     change_name_if_conflict=True)
    api.project.update_meta(dst_project.id, g.project_meta.to_json())
    datasets = api.dataset.get_list(g.PROJECT_ID)

    for dataset in datasets:
        dst_dataset = api.dataset.create(dst_project.id, dataset.name)
        images_infos = api.image.get_list(dataset.id)
        for batch in sly.batched(images_infos):
            image_ids = [image_info.id for image_info in images_infos]
            ann_infos = api.annotation.download_batch(dataset.id, image_ids)

            image_nps = api.image.download_nps(dataset.id, image_ids)
            anns = [sly.Annotation.from_json(ann_info.annotation, g.project_meta) for ann_info in ann_infos]
            crops = f.crop_and_resize_objects(image_nps, anns, state)
            crop_nps, crop_anns = f.unpack_crops(crops)
            crop_names = f.get_names_from_crop_anns(crop_anns)

            dst_image_infos = api.image.upload_nps(dst_dataset.id, crop_names, crop_nps)
            dst_image_ids = [dst_image_info.id for dst_image_info in dst_image_infos]
            api.annotation.upload_anns(dst_image_ids, crop_anns)






def main():
    data = {}
    state = {}

    init_ui.init(data, state)

    initial_events = [
        {
            "state": state,
            "context": None,
            "command": "preview",
        }
    ]

    # Run application service
    g.my_app.run(data=data, state=state, initial_events=initial_events)


if __name__ == "__main__":
    sly.main_wrapper("main", main)
