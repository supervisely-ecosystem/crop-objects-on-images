import os
import globals as g
import supervisely_lib as sly


def resize_crop(img, ann, out_size):
    img = sly.image.resize(img, out_size)
    ann = ann.resize(out_size)
    return img, ann


def crop_and_resize_objects(img_nps, anns, app_state):
    crops = []
    for img_np, ann in zip(img_nps, anns):
        if len(ann.labels) == 0:
            continue

        selected_classes = ["kiwi", "lemon"]
        crop_padding = {
            "top": "{}%".format(app_state["cropPadding"]),
            "left": "{}%".format(app_state["cropPadding"]),
            "right": "{}%".format(app_state["cropPadding"]),
            "bottom": "{}%".format(app_state["cropPadding"])
        }

        for class_name in selected_classes:
            objects_crop = sly.aug.instance_crop(img_np, ann, class_name, False, crop_padding)
            if app_state["autoSize"] is False:
                resized_crop = []
                for crop_img, crop_ann in objects_crop:
                    crop_img, crop_ann = resize_crop(crop_img, crop_ann, (app_state["inputHeight"], app_state["inputWidth"]))

                    resized_crop.append((crop_img, crop_ann))
                crops.append(resized_crop)
            else:
                crops.append(objects_crop)

    flat_crops = []
    for sublist in crops:
        for crop in sublist:
            flat_crops.append(crop)

    return flat_crops


def unpack_crops(crops):
    img_nps = []
    anns = []
    for img_np, ann in crops:
        img_nps.append(img_np)
        anns.append(ann)
    return img_nps, anns


def get_names_from_crop_anns(crop_anns):
    crop_names = []
    name_idx = 0
    for ann in crop_anns:
        for label in ann.labels:
            name_idx += 1
            crop_names.append(f"{label.obj_class.name}_{name_idx}.png")
    return crop_names


@sly.timeit
def upload_augs(crops):
    if len(crops) == 0:
        g.api.task.set_fields(g.TASK_ID, [{"field": "data.showEmptyMessage", "payload": True}])
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
        if hasattr(monitor, 'last_percent') is False:
            monitor.last_percent = 0
        cur_percent = int(monitor.bytes_read * 100.0 / monitor.len)
        if cur_percent - monitor.last_percent > 15 or cur_percent == 100:
            g.api.task.set_fields(g.TASK_ID, [{"field": "data.previewProgress", "payload": cur_percent}])
            monitor.last_percent = cur_percent

    upload_results = g.api.file.upload_bulk(g.TEAM_ID, upload_src_paths, upload_dst_paths, _progress_callback)
    #clean local data
    for local_path in upload_src_paths:
        sly.fs.silent_remove(local_path)
    return upload_results
