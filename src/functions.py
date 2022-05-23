import supervisely as sly
from supervisely.io.fs import get_file_name

import globals as g


def resize_crop(img, ann, out_size):
    img = sly.image.resize(img, out_size)
    ann = ann.resize(out_size)
    return img, ann


def unpack_single_crop(crop, image_name):
    crop = crop[0][image_name]
    flat_crops = []
    for sublist in crop:
        for crop in sublist:
            flat_crops.append(crop)

    return flat_crops


def crop_and_resize_objects(img_nps, anns, app_state, selected_classes, original_names):
    crops = []
    crop_padding = {
        "top": "{}%".format(app_state["cropPadding"]),
        "left": "{}%".format(app_state["cropPadding"]),
        "right": "{}%".format(app_state["cropPadding"]),
        "bottom": "{}%".format(app_state["cropPadding"]),
    }
    for img_np, ann, original_name in zip(img_nps, anns, original_names):
        img_dict = {original_name: []}
        if len(ann.labels) == 0:
            crops.append(img_dict)
            continue

        for class_name in selected_classes:
            objects_crop = sly.aug.instance_crop(
                img_np, ann, class_name, False, crop_padding
            )
            if app_state["autoSize"] is False:
                resized_crop = []
                for crop_img, crop_ann in objects_crop:
                    crop_img, crop_ann = resize_crop(
                        crop_img,
                        crop_ann,
                        (app_state["inputHeight"], app_state["inputWidth"]),
                    )
                    resized_crop.append((crop_img, crop_ann))
                img_dict[original_name].append(resized_crop)
            else:
                img_dict[original_name].append(objects_crop)

        crops.append(img_dict)
    return crops


def unpack_crops(crops, original_names):
    img_nps = []
    anns = []
    img_names = []
    name_idx = 0
    for crop, original_name in zip(crops, original_names):
        for label_crop in crop[original_name]:
            for img_np, ann in label_crop:
                img_nps.append(img_np)
                anns.append(ann)
                for label in ann.labels:
                    name_idx += 1
                    img_names.append(
                        f"{get_file_name(original_name)}_{label.obj_class.name}_{name_idx}_{label.obj_class.sly_id}.png"
                    )

    return img_nps, anns, img_names


def get_selected_classes_from_ui(selected_classes):
    classes = []
    ui_classes = g.api.task.get_field(g.TASK_ID, "data.classes")
    for obj_class, is_selected in zip(ui_classes, selected_classes):
        if is_selected:
            classes.append(obj_class["name"])
    return classes


@sly.timeit
def upload_preview(crops):
    if len(crops) == 0:
        g.api.task.set_fields(
            g.TASK_ID, [{"field": "data.showEmptyMessage", "payload": True}]
        )
        return

    upload_src_paths = []
    upload_dst_paths = []
    for idx, (cur_img, cur_ann) in enumerate(crops):
        img_name = "{:03d}.png".format(idx)
        remote_path = "/temp/{}/{}".format(g.TASK_ID, img_name)
        if g.api.file.exists(g.TEAM_ID, remote_path):
            g.api.file.remove(g.TEAM_ID, remote_path)
        local_path = "{}/{}".format(g.my_app.data_dir, img_name)
        sly.image.write(local_path, cur_img)
        upload_src_paths.append(local_path)
        upload_dst_paths.append(remote_path)

    g.api.file.remove(g.TEAM_ID, "/temp/{}/".format(g.TASK_ID))

    def _progress_callback(monitor):
        if hasattr(monitor, "last_percent") is False:
            monitor.last_percent = 0
        cur_percent = int(monitor.bytes_read * 100.0 / monitor.len)
        if cur_percent - monitor.last_percent > 15 or cur_percent == 100:
            g.api.task.set_fields(
                g.TASK_ID, [{"field": "data.previewProgress", "payload": cur_percent}]
            )
            monitor.last_percent = cur_percent

    upload_results = g.api.file.upload_bulk(
        g.TEAM_ID, upload_src_paths, upload_dst_paths, _progress_callback
    )
    # clean local data
    for local_path in upload_src_paths:
        sly.fs.silent_remove(local_path)
    return upload_results


def copy_tags(crop_anns, save_anns):
    new_anns = []
    for ann in crop_anns:
        for label in ann.labels:
            label_tags = label.tags
            if save_anns:
                new_ann = ann.add_tags(label_tags)
            else:
                new_ann = ann.clone(img_size=ann.img_size, labels=[], img_tags=label_tags)
            new_anns.append(new_ann)
    return new_anns
