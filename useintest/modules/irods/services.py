import json
import logging
import math
import os
from abc import abstractmethod, ABCMeta
from typing import List, Type, Callable, Sequence

from useintest.modules.irods.models import IrodsUser, IrodsDockerisedService, Version
from useintest.services.controllers import DockerisedServiceController

_DOCKER_REPOSITORY = "mercury/icat"

_logger = logging.getLogger(__name__)



class IrodsBaseServiceController(DockerisedServiceController[IrodsDockerisedService], metaclass=ABCMeta):
    """
    TODO
    """
    @staticmethod
    @abstractmethod
    def write_connection_settings(file_location: str, service: IrodsDockerisedService):
        """
        Writes the connection settings for the given iRODS service to the given location.
        :param file_location: the location to write the settings to (file should not already exist)
        :param service: the Dockerized iRODS service
        """

    @staticmethod
    def _persistent_error_log_detector(line: str) -> bool:
        """
        TODO
        :param line:
        :return:
        """
        return "No space left on device" in line

    def __init__(self, version: Version, users: Sequence[IrodsUser], config_file_name: str,
                 repository: str, tag: str, ports: List[int], start_log_detector: Callable[[str], bool], **kwargs):
        """
        Constructor.
        :param version:
        :param users:
        :param config_file_name:
        :param repository:
        :param tag:
        :param ports:
        :param start_log_detector:
        :param kwargs:
        """
        super().__init__(
            IrodsDockerisedService, repository, tag, ports, start_log_detector=start_log_detector, **kwargs)
        self.config_file_name = config_file_name
        self._version = version
        self._users = users

    def start_service(self) -> IrodsDockerisedService:
        service = super().start_service()
        for user in self._users:
            if user.admin:
                service.root_user = user
            service.users.add(user)
        service.version = self._version
        return service


class Irods4ServiceController(IrodsBaseServiceController, metaclass=ABCMeta):
    """
    iRODS 4 service controller.
    """
    _PORT = 1247
    _CONFIG_FILE_NAME = "irods_environment.json"
    _NATIVE_AUTHENTICATION_SCHEME = "native"

    _HOST_PARAMETER_NAME = "irods_host"
    _PORT_PARAMETER_NAME = "irods_port"
    _USERNAME_PARAMETER_NAME = "irods_user_name"
    _ZONE_PARAMETER_NAME = "irods_zone_name"
    _AUTHENTICATION_SCHEME_PARAMETER_NAME = "irods_authentication_scheme"

    _USERS = [IrodsUser("rods", "testZone", "irods123", admin=True)]

    # TODO: These connection settings will not work with port-mapping to localhost
    @staticmethod
    def write_connection_settings(file_location: str, service: IrodsDockerisedService):
        if os.path.isfile(file_location):
            raise ValueError(f"Settings cannot be written to a file that already exists ({file_location})")

        config = {Irods4ServiceController._USERNAME_PARAMETER_NAME: service.root_user.username,
                  Irods4ServiceController._HOST_PARAMETER_NAME: service.name,
                  Irods4ServiceController._PORT_PARAMETER_NAME: Irods4ServiceController._PORT,
                  Irods4ServiceController._ZONE_PARAMETER_NAME: service.root_user.zone,
                  Irods4ServiceController._AUTHENTICATION_SCHEME_PARAMETER_NAME:
                      Irods4ServiceController._NATIVE_AUTHENTICATION_SCHEME}
        config_as_json = json.dumps(config)
        _logger.debug(f"Writing iRODS connection config to: {file_location}")
        with open(file_location, "w") as settings_file:
            settings_file.write(config_as_json)

    def __init__(self, docker_repository: str, docker_tag: str, start_timeout: int=math.inf, start_tries: int=10,
                 version: Version=None):
        """
        Constructor.
        :param docker_repository: name of the Docker repository
        :param docker_tag: the Docker tag of the iRODS 4 image
        :param start_timeout: see `ContainerisedServiceController.__init__`
        :param start_tries: see `ContainerisedServiceController.__init__`
        :param version: exact version of the iRODS 4 sever (will use `docker_tag` if not supplied)
        """
        version = version if version is not None else Version(docker_tag)
        super().__init__(version, Irods4ServiceController._USERS, Irods4ServiceController._CONFIG_FILE_NAME,
                         docker_repository, docker_tag, [Irods4ServiceController._PORT],
                         start_log_detector=lambda line: "iRODS server started successfully!" in line,
                         transient_error_log_detector=lambda line: "iRODS server failed to start." in line
                                                                   or "RuntimeError:" in line,
                         persistent_error_log_detector=IrodsBaseServiceController._persistent_error_log_detector,
                         start_timeout=start_timeout, start_tries=start_tries)


# TODO: Why not use DockerisedServiceControllerTypeBuilder?
def build_irods_service_controller_type(docker_repository: str, docker_tag: str, superclass: type) \
        -> Type[IrodsBaseServiceController]:
    """
    Builds a controller for an iRODS server that runs in containers of on the given Docker image.
    :param docker_repository: name of the Docker repository
    :param docker_tag: the Docker tag of the image in the Docker repository
    :param superclass: the superclass of the service controller
    :return: the build service controller for the given image
    """
    def init(self: superclass, *args, **kwargs):
        super(type(self), self).__init__(docker_repository, docker_tag, *args, **kwargs)

    return type(
        "Irods%sServiceController" % docker_tag.replace(".", "_"),
        (superclass,),
        {"__init__": init}
    )


# Concrete service controller definitions
Irods4_1_10ServiceController = build_irods_service_controller_type(_DOCKER_REPOSITORY, "4.1.10", Irods4ServiceController)
IrodsServiceController = Irods4_1_10ServiceController

irods_service_controllers = {Irods4_1_10ServiceController}
