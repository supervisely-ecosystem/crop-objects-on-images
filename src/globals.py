import os
import sys
from pathlib import Path

import supervisely as sly
# from dotenv import load_dotenv
from supervisely.app.v1.app_service import AppService

root_source_dir = str(Path(sys.argv[0]).parents[1])
print(f"App source directory: {root_source_dir}")
sys.path.append(root_source_dir)

# only for convenient debug
# debug_env_path = os.path.join(root_source_dir, "debug.env")
# secret_debug_env_path = os.path.join(root_source_dir, "secret_debug.env")
# load_dotenv(debug_env_path)
# load_dotenv(secret_debug_env_path, override=True)


my_app = AppService()
api: sly.Api = my_app.public_api

TASK_ID = int(os.environ["TASK_ID"])
TEAM_ID = int(os.environ["context.teamId"])
WORKSPACE_ID = int(os.environ["context.workspaceId"])
PROJECT_ID = int(os.environ["modal.state.slyProjectId"])


project_info = api.project.get_info_by_id(PROJECT_ID)
project_meta_json = api.project.get_meta(project_info.id)
project_meta = sly.ProjectMeta.from_json(project_meta_json)


CNT_GRID_COLUMNS = 3

image_grid_options = {
    "opacity": 0.5,
    "fillRectangle": False,
    "enableZoom": False,
    "syncViews": False,
}

total_images_count = api.project.get_images_count(project_info.id)
res_project_name = f"{project_info.name}(cropped_objects)"


image_ids = []
for dataset in api.dataset.get_list(project_info.id):
    image_infos = api.image.get_list(dataset.id)
    image_ids.extend([info.id for info in image_infos])

my_app.logger.info("Image ids are initialized", extra={"count": len(image_ids)})
