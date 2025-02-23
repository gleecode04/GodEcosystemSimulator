# backend/ml/train_aml.py

import os
from azureml.core import Workspace, Experiment, ScriptRunConfig, Environment, ComputeTarget
from azureml.core.environment import CondaDependencies
import subprocess

# 1. Connect to AML workspace using azure_config.json
ws = Workspace.from_config(path="azure_config.json")  # or .azureml/config.json

# 2. Create a Python environment
aml_env = Environment("hacklytics-env")
cd = CondaDependencies()
cd.add_pip_package("pandas")
cd.add_pip_package("scikit-learn")
cd.add_pip_package("azure-storage-blob")
cd.add_pip_package("joblib")
cd.add_pip_package("dotenv")
cd.add_pip_package("pyyaml")
aml_env.python.conda_dependencies = cd

# 3. Specify compute target
compute_target_name = "gpu-dev-instance"  # or "gpu-cluster" if you created a cluster
compute_target = ComputeTarget(workspace=ws, name=compute_target_name)

# 4. Create a ScriptRunConfig pointing to train.py
# We'll run the same train.py, but in AML environment
src = ScriptRunConfig(
    source_directory="./ml",
    script="train.py",     # We'll reuse our local train.py
    compute_target=compute_target,
    environment=aml_env
)

# 5. Submit experiment
experiment = Experiment(ws, "hacklytics-train")
run = experiment.submit(src)
print("Submitted run... waiting for completion")
run.wait_for_completion(show_output=True)

# Download outputs (model, logs) from the run
artifacts_dir = "outputs_from_run"
os.makedirs(artifacts_dir, exist_ok=True)
run.download_files(output_directory=artifacts_dir)
print(f"Run artifacts downloaded to {artifacts_dir}")
