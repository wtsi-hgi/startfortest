from bringupfortest.models import Container
from hgicommon.docker.client import create_client

_docker_client = create_client()


def is_docker_container_running(container: Container) -> bool:
    """
    TODO
    :param container:
    :return:
    """
    return _docker_client.inspect_container(container.native_object)["State"]["Status"] == "running"
