import logging
import os
import tarfile
from abc import ABCMeta
from io import BytesIO
from pathlib import PurePosixPath
from time import sleep
from typing import Generic

from useintest.services.builders import DockerisedServiceControllerTypeBuilder
from useintest.services.controllers import DockerisedServiceController, DockerisedServiceWithUsersType
from useintest.services.models import User, DockerisedServiceWithUsers

_CONFIGURATION_HOST_LOCATION = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_resources/data")
_CONFIGURATION_DOCKER_LOCATION = PurePosixPath("/data")

_ROOT_USERNAME = "root"
_ROOT_PASSWORD = "root"


class GogsBaseServiceController(Generic[DockerisedServiceWithUsersType],
                                DockerisedServiceController[DockerisedServiceWithUsersType], metaclass=ABCMeta):
    """
    Base class for Gogs service controllers.
    """
    def start_service(self) -> DockerisedServiceWithUsersType:
        service = super().start_service()
        container = service.container

        # Painful conversion required due to limitation of the Docker client:
        # https://github.com/docker/docker-py/issues/1027#issuecomment-299654299
        archive_container = BytesIO()
        with tarfile.open(mode="w", fileobj=archive_container) as archive:
            archive.add(_CONFIGURATION_HOST_LOCATION, arcname=_CONFIGURATION_DOCKER_LOCATION.name)
        archive_as_bytes = bytes(archive_container.getbuffer())

        # Add configuration
        container.put_archive(_CONFIGURATION_DOCKER_LOCATION.parent.as_posix(), archive_as_bytes)
        service.root_user = User(_ROOT_USERNAME, _ROOT_PASSWORD)

        # Start gogs
        _, output_generator = container.exec_run(["/app/gogs/docker/start.sh"], stream=True)
        for line in output_generator:
            logging.debug(line)
            if "Listen: http://0.0.0.0:3000" in str(line):
                break

        return service


# Employing hacky way of getting run sleeping forever with the detector
common_setup = {
    "superclass": GogsBaseServiceController,
    "service_model": DockerisedServiceWithUsers[User],
    "repository": "gogs/gogs",
    "start_log_detector": lambda log_line: "127.0.0.1\tlocalhost" in log_line,
    "transient_error_log_detector": lambda log_line: "the container has stopped" in log_line,
    "ports": [3000],
    "additional_run_settings": {"entrypoint": "tail", "command": ["-f", "/etc/hosts"]}
}

Gogs0_11_4ServiceController = DockerisedServiceControllerTypeBuilder(
    name="Gogs0_11_4ServiceController",
    tag="0.11.4",
    **common_setup).build()

GogsServiceController = Gogs0_11_4ServiceController

gogs_service_controllers = {Gogs0_11_4ServiceController}
