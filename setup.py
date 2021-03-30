from setuptools import setup, find_packages


setup(
    name="mlflow-google",
    version="0.0.1",
    description="Google Cloud Platform plugin for MLflow",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    # Require MLflow as a dependency of the plugin, so that plugin users can simply install
    # the plugin & then immediately use it with MLflow
    install_requires=[
        "mlflow",
        # Update to 'google-cloud-aiplatform' once Model Builder SDK is pushed to PyPi
        "google-cloud-aiplatform @ git+ssh://git@github.com/googleapis/python-aiplatform@mb-release#egg=google-cloud-aiplatform",

    ],
    entry_points={
        # Define a Model Registry Store plugin for tracking URIs with scheme 'file-plugin'
        # "mlflow.model_registry_store": "aiplatform=mlflow_google.ai_platform_store:PluginRegistrySqlAlchemyStore",  # noqa
        # Define a MLflow model deployment plugin for target 'faketarget'
        "mlflow.deployments": "aiplatform=mlflow_google.ai_platform_deployment_plugin:AiPlatformStore",
    },
)
