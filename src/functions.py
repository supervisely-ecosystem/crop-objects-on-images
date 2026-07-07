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


def crop_objects_on_image(img_np, ann, class_name, include_overlapping, padding_percent):
    results = []
    img_rect = sly.Rectangle.from_size(img_np.shape[:2])
    for label in ann.labels:
        if label.obj_class.name != class_name:
            continue
        bbox = label.geometry.to_bbox()
        pad_h = int(bbox.height * padding_percent / 100)
        pad_w = int(bbox.width * padding_percent / 100)
        # bottom/right extended by 1 extra px to keep crop sizes identical to
        # sly.aug.instance_crop used before
        rect = sly.Rectangle(
            bbox.top - pad_h,
            bbox.left - pad_w,
            bbox.bottom + pad_h + 1,
            bbox.right + pad_w + 1,
        )
        crops = rect.crop(img_rect)
        if len(crops) == 0:
            continue
        rect = crops[0]
        image_crop = sly.image.crop(img_np, rect)
        labels_to_keep = ann.labels if include_overlapping else [label]
        cropped_ann = ann.clone(labels=labels_to_keep).relative_crop(rect)
        results.append((image_crop, cropped_ann, label))
    return results


def crop_and_resize_objects(img_nps, anns, app_state, selected_classes, original_names):
    crops = []
    include_overlapping = app_state["keepAnns"] and app_state["includeOverlapping"]
    for img_np, ann, original_name in zip(img_nps, anns, original_names):
        img_dict = {original_name: []}
        if len(ann.labels) == 0:
            crops.append(img_dict)
            continue

        for class_name in selected_classes:
            objects_crop = crop_objects_on_image(
                img_np, ann, class_name, include_overlapping, app_state["cropPadding"]
            )
            if app_state["autoSize"] is False:
                resized_crop = []
                for crop_img, crop_ann, target_label in objects_crop:
                    crop_img, crop_ann = resize_crop(
                        crop_img,
                        crop_ann,
                        (app_state["inputHeight"], app_state["inputWidth"]),
                    )
                    resized_crop.append((crop_img, crop_ann, target_label))
                img_dict[original_name].append(resized_crop)
            else:
                img_dict[original_name].append(objects_crop)

        crops.append(img_dict)
    return crops


def unpack_crops(crops, original_names):
    img_nps = []
    anns = []
    img_names = []
    target_labels = []
    name_idx = 0
    for crop, original_name in zip(crops, original_names):
        for label_crop in crop[original_name]:
            for img_np, ann, target_label in label_crop:
                img_nps.append(img_np)
                anns.append(ann)
                target_labels.append(target_label)
                name_idx += 1
                img_names.append(
                    f"{get_file_name(original_name)}_{target_label.obj_class.name}_{name_idx}_{target_label.obj_class.sly_id}.png"
                )

    return img_nps, anns, img_names, target_labels


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


def copy_tags(crop_anns, target_labels, save_anns):
    new_anns = []
    for ann, target_label in zip(crop_anns, target_labels):
        label_tags = target_label.tags
        if save_anns:
            new_ann = ann.add_tags(label_tags)
        else:
            new_ann = ann.clone(img_size=ann.img_size, labels=[], img_tags=label_tags)
        new_anns.append(new_ann)
    return new_anns


def validate_tags(project_meta):
    need_update = False
    for tag_meta in project_meta.tag_metas:
        if tag_meta.applicable_to == sly.TagApplicableTo.OBJECTS_ONLY:
            new_tag_meta = tag_meta.clone(applicable_to=sly.TagApplicableTo.ALL)
            project_meta = project_meta.delete_tag_meta(tag_meta.name)
            project_meta = project_meta.add_tag_meta(new_tag_meta)
            if need_update is False:
                need_update = True

    return project_meta, need_update
