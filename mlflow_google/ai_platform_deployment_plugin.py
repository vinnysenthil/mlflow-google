import os
import docker
import logging

from mlflow.deployments import BaseDeploymentClient
from mlflow.models.cli import _get_flavor_backend
from mlflow.pyfunc.scoring_server import FORCE_TF_SERVING_OUTPUT 


from google.cloud import aiplatform

from typing import Dict

f_deployment_name = "fake_deployment_name"

_logger = logging.getLogger(__name__)

class AiPlatformDeploymentClient(BaseDeploymentClient):

    def __init__(self, project=None, location=None, credentials=None):

        aiplatform.init(
            project=project,
            location=location,
            credentials=credentials
        )

        self.aiplatform = aiplatform

        super.__init__()

    @property
    def project(self):
        """Name of Google Cloud project to deploy model in."""
        return self._project

    @property
    def location(self):
        """Location of Google Cloud AI Platform service to deploy model"""
        return self._location

    def _build_serving_image(
        self,
        model_uri: str,
        destination_image_uri: str,
        mlflow_source_dir: str=None
    ):
        _logger.info("Building image")
        flavor_backend = _get_flavor_backend(model_uri)
        flavor_backend.build_image(
            model_uri,
            destination_image_uri,
            install_mlflow=mlflow_source_dir is not None,
            mlflow_home=mlflow_source_dir
        )
        _logger.info("Uploading image to Google Container Registry")

        client = docker.from_env()
        result = client.images.push(
            destination_image_uri,
            stream=True,
            decode=True
        )
        for line in result:
            # Docker client doesn't catch auth errors, so we have to do it
            # ourselves. See https://github.com/docker/docker-py/issues/1772
            if 'errorDetail' in line:
                raise docker.errors.APIError(
                    line['errorDetail']['message']
                )
            if 'status' in line:
                print(line['status'])
    
    def _upload_model(self, display_name, image_uri, model_options):

        if model_options:
            model_cfg.update(model_options)

        _logger.info(
            "Uploading config to Google Cloud AI Platform: %s/models/%s",
            model_parent,
            display_name
        )

        deployed_model = self.aiplatform.Model.upload(
            display_name=display_name,
            serving_container_image_uri=image_uri,
            serving_container_predict_route="/invocations",
            serving_container_health_route="/ping",
            serving_container_ports=[8080],
            serving_container_environment_variables={
                FORCE_TF_SERVING_OUTPUT: "True"
            }
        )

        return deployed_model

    def create_deployment(self, name: str, model_uri: str, flavor:str=None, config:Dict[str, str]=None):
        if config and config.get("raiseError") == "True":
            raise RuntimeError("Error requested")

        # Fetch artifacts from MLFlow model URI
        # Build + push container, upload model
        # Create endpoint

        new_deployment = aiplatform.Endpoint.create(
            display_name=f"{}/{}/{}",
            description="Model deployed from MLFlow",
            labels={
                "is_mlflow_deployment": "true",
                "mlflow_deployment_name": name,
            }
        )

        # Deploy custom container Model to new endpoint

        return {"name": f_deployment_name, "flavor": flavor}

    def delete_deployment(self, name):
        # Locate deployment endpoint from MLFlow deployment list
        # Call Endpoint.delete(force=True), will undeploy all models on Endpoint first
        return None

    def update_deployment(self, name, model_uri=None, flavor=None, config=None):
        # Endpoint.update
        return {"flavor": flavor}

    def list_deployments(self):
        if os.environ.get("raiseError") == "True":
            raise RuntimeError("Error requested")
        
        # Fetch and return all MLFlow deployment endpoints
        return [f_deployment_name]

    def get_deployment(self, name):
        # Fetch MLFlow deployment endpoints
        # Return endpoint where display_name == name
        return {"key1": "val1", "key2": "val2"}

    def predict(self, deployment_name, df):
        return "1"


def run_local(name, model_uri, flavor=None, config=None):
    print(
        "Deployed locally at the key {} using the model from {}. ".format(name, model_uri)
        + "It's flavor is {} and config is {}".format(flavor, config)
    )


def target_help():
    return "Target help is called"