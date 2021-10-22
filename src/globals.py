import os
import supervisely_lib as sly

my_app = sly.AppService()
api: sly.Api = my_app.public_api

TASK_ID = int(os.environ["TASK_ID"])
TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])
PROJECT_ID = int(os.environ['modal.state.slyProjectId'])


project_info = api.project.get_info_by_id(PROJECT_ID)
project_meta_json = api.project.get_meta(project_info.id)
project_meta = sly.ProjectMeta.from_json(project_meta_json)


CNT_GRID_COLUMNS = 3

image_grid_options = {
    "opacity": 0.5,
    "fillRectangle": False,
    "enableZoom": False,
    "syncViews": False
}

total_images_count = api.project.get_images_count(project_info.id)
res_project_name = f"{project_info.name}(cropped_objects)"


image_ids = []
for dataset in api.dataset.get_list(project_info.id):
    image_infos = api.image.get_list(dataset.id)
    image_ids.extend([info.id for info in image_infos])

my_app.logger.info("Image ids are initialized", extra={"count": len(image_ids)})


