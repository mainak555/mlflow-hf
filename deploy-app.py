
from huggingface_hub import HfApi
from util import create_hf_repo
import os

hfApi = HfApi(token=os.getenv("HF_TOKEN"))
hf_repo = os.getenv('HF_REPO')

# Create HF Space
create_hf_repo(hfApi, hf_repo, "space")

# Adding Secrets to Space
for key in ["MLFLOW_TRACKING_PASSWORD", "MLFLOW_TRACKING_USERNAME", "MLFLOW_MYSQL_CONN", "MLFLOW_MYSQL_CA"]:
    hfApi.add_space_secret(
        value=os.getenv(key),
        repo_id=hf_repo,
        key=key
    )

# Deploying MLFlow
hfApi.upload_folder(
    ignore_patterns=["*pycache**/", ".env"],
    folder_path="./app",
    repo_type="space",
    repo_id=hf_repo
)
