from startfortest.models import Container
from hgicommon.docker.client import create_client

_docker_client = create_client()


def is_docker_container_running(container: Container) -> bool:
    """
    Returns whether the Docker container, referenced by the given container, is running.
    :param container: the container model
    :return: whether the container is running
    """
    return _docker_client.inspect_container(container.native_object)["State"]["Status"] == "running"
