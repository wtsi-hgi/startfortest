from docker.errors import NotFound
from hgicommon.docker.client import create_client

from useintest.services.models import DockerisedService

try:
    _docker_client = create_client()
    docker_running = isinstance(_docker_client.info(), dict)
except Exception:
    docker_running = False


def is_docker_container_running(service: DockerisedService) -> bool:
    """
    Returns whether the Docker container, referenced by the given container, is running.
    :param service: the service model
    :return: whether the container is running
    """
    try:
        return _docker_client.inspect_container(service.container)["State"]["Status"] == "running"
    except NotFound:
        return False
