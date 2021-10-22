import globals as g
import supervisely_lib as sly


def validate_input_meta(meta: sly.ProjectMeta):
    classes_with_unsupported_shape = []
    if len(meta.obj_classes) == 0:
        raise ValueError("There are no classes in project")

    for obj_class in meta.obj_classes:
        if obj_class.geometry_type == sly.Point or obj_class.geometry_type == sly.PointLocation:
            classes_with_unsupported_shape.append((obj_class.name, obj_class.geometry_type.geometry_name()))

    if len(classes_with_unsupported_shape) > 0:
        sly.logger.warn(f'Unsupported shapes: {classes_with_unsupported_shape}. '
                        f'App supports only {sly.Bitmap.geometry_name()}, {sly.Rectangle.geometry_name()}, {sly.Polygon.geometry_name()}, {sly.Polyline.geometry_name()}, {sly.AnyGeometry.geometry_name()}. '
                        'Use another apps to transform class shapes or rasterize objects. Learn more in app readme.')


def prepare_ui_classes(project_meta):
    ui_classes = []
    classes_selected = []
    for obj_class in project_meta.obj_classes:
        if obj_class.geometry_type == sly.Point or obj_class.geometry_type == sly.PointLocation or obj_class.geometry_type == sly.Cuboid:
            continue
        obj_class: sly.ObjClass
        ui_classes.append(obj_class.to_json())
        classes_selected.append(True)
    return ui_classes, classes_selected, [False] * len(classes_selected)


ui_classes, classes_selected, classes_disabled = prepare_ui_classes(g.project_meta)


def init(data, state):
    data["projectId"] = g.project_info.id
    data["projectName"] = g.project_info.name
    data["classes"] = ui_classes
    data["projectPreviewUrl"] = g.api.image.preview_url(g.project_info.reference_image_url, 100, 100)
    data["progress"] = 0
    data["started"] = False
    data["totalImagesCount"] = g.total_images_count
    data["preview"] = {"content": {}, "options": g.image_grid_options}
    data["previewProgress"] = 0
    data["showEmptyMessage"] = False
    data["finished"] = False

    state["cropPadding"] = 0
    state["keepAnns"] = True
    state["classesSelected"] = classes_selected
    state["classesDisabled"] = classes_disabled
    state["autoSize"] = True
    state["inputWidth"] = 256
    state["inputHeight"] = 256
    state["resultProjectName"] = g.res_project_name
