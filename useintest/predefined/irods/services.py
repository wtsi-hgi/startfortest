import json
import logging
import math
import os
from abc import abstractmethod, ABCMeta
from time import sleep
from typing import List, Type, Callable, Sequence

from hgicommon.docker.client import create_client
from useintest.predefined.irods.models import IrodsUser, IrodsDockerisedService, Version
from useintest.services.controllers import DockerisedServiceController
from useintest.services.models import DockerisedService

_logger = logging.getLogger(__name__)

_DOCKER_REPOSITORY = "mercury/icat"


class IrodsBaseServiceController(DockerisedServiceController, metaclass=ABCMeta):
    """
    TODO
    """
    @staticmethod
    @abstractmethod
    def write_connection_settings(file_location: str, service: IrodsDockerisedService) -> str:
        """
        Writes the connection settings for the given iRODS service to the given location.
        :param file_location: the location to write the settings to (file should not already exist)
        :param service: the Dockerized iRODS service
        """

    @staticmethod
    def _persistent_error_detector(log_line: str) -> bool:
        """
        TODO
        :param log_line:
        :return:
        """
        return "No space left on device" in log_line

    def __init__(self, version: Version, users: Sequence[IrodsUser], config_file_name: str,
                 repository: str, tag: str, ports: List[int], start_detector: Callable[[str], bool], **kwargs):
        """
        Constructor.
        :param version:
        :param users:
        :param config_file_name:
        :param repository:
        :param tag:
        :param ports:
        :param start_detector:
        :param kwargs:
        """
        super().__init__(IrodsDockerisedService, repository, tag, ports, start_detector, **kwargs)
        self.config_file_name = config_file_name
        self._version = version
        self._users = users

    def start_service(self) -> IrodsDockerisedService:
        service = super().start_service()
        service.users = self._users
        service.version = self._version
        return service


class Irods3ServiceController(IrodsBaseServiceController, metaclass=ABCMeta):
    """
    iRODS 3 service controller.
    """
    _PORT = 1247
    _CONFIG_FILE_NAME = ".irodsEnv"

    _HOST_PARAMETER_NAME = "irodsHost"
    _PORT_PARAMETER_NAME = "irodsPort"
    _USERNAME_PARAMETER_NAME = "irodsUserName"
    _ZONE_PARAMETER_NAME = "irodsZone"

    _USERS = [IrodsUser("rods", "iplant", "rods", admin=True)]

    @staticmethod
    def write_connection_settings(file_location: str, service: IrodsDockerisedService) -> str:
        if os.path.isfile(file_location):
            raise ValueError("Settings cannot be written to a file that already exists")

        user = service.users[0]
        config = [
            (Irods3ServiceController._USERNAME_PARAMETER_NAME, user.username),
            (Irods3ServiceController._HOST_PARAMETER_NAME, service.name),
            (Irods3ServiceController._PORT_PARAMETER_NAME, Irods3ServiceController._PORT),
            (Irods3ServiceController._ZONE_PARAMETER_NAME, user.zone)
        ]
        _logger.debug("Writing iRODS connection config to: %s" % file_location)
        with open(file_location, "w") as settings_file:
            settings_file.write("\n".join(["%s %s" % x for x in config]))

        return user.password

    @staticmethod
    def _start_detector(log_line: str) -> bool:
        """
        TODO
        :param log_line:
        :return:
        """
        return "exited: irods" in log_line

    @staticmethod
    def _transient_error_detector(log_line: str) -> bool:
        """
        TODO
        :param log_line:
        :return:
        """
        return "failed to start" in log_line or "exited: irods" in log_line and "not expected" in log_line

    # TODO: Use default `start_timeout` and `start_tries` values from superclass
    def __init__(self, docker_repository: str, docker_tag: str, start_timeout: int=math.inf, start_tries: int=10,
                 version: Version=None):
        """
        Constructor.
        :param docker_repository: name of the Docker repository
        :param docker_tag: tag of the Docker image that will run the iRODS 4 server
        :param start_timeout: see `ContainerisedServiceController.__init__`
        :param start_tries: see `ContainerisedServiceController.__init__`
        :param version: exact version of the iRODS 4 sever (will use `docker_tag` if not supplied)
        """
        version = version if version is not None else Version(docker_tag)
        super().__init__(version, Irods3ServiceController._USERS, Irods3ServiceController._CONFIG_FILE_NAME,
                         docker_repository, docker_tag, [Irods3ServiceController._PORT],
                         Irods3ServiceController._start_detector,
                         transient_error_detector=Irods3ServiceController._transient_error_detector,
                         persistent_error_detector=IrodsBaseServiceController._persistent_error_detector,
                         start_timeout=start_timeout, start_tries=start_tries)

    def _wait_until_started(self, container: DockerisedService) -> bool:
        if super()._wait_until_started(container) is False:
            return False

        # Just because iRODS says it has started, it does not mean it is ready to do queries!
        docker_client = create_client()
        status_query = docker_client.exec_create(
            container.name, "su - irods -c \"/home/irods/iRODS/irodsctl --verbose status\"", stdout=True)
        while "No servers running" in docker_client.exec_start(status_query).decode("utf8"):
            # Nothing else to check on - just sleep it out
            _logger.info("Still waiting on iRODS setup")
            sleep(0.1)

        return True


class Irods4ServiceController(IrodsBaseServiceController, metaclass=ABCMeta):
    """
    iRODS 4 service controller.
    """
    _PORT = 1247
    _CONFIG_FILE_NAME = "irods_environment.json"

    _HOST_PARAMETER_NAME = "irods_host"
    _PORT_PARAMETER_NAME = "irods_port"
    _USERNAME_PARAMETER_NAME = "irods_user_name"
    _ZONE_PARAMETER_NAME = "irods_zone_name"

    _USERS = [
        IrodsUser("rods", "testZone", "irods123", admin=True)
    ]

    # TODO: These connection settings will not work with port-mapping to localhost
    @staticmethod
    def write_connection_settings(file_location: str, service: IrodsDockerisedService) -> str:
        if os.path.isfile(file_location):
            raise ValueError("Settings cannot be written to a file that already exists (%s)" % file_location)

        user = service.users[0]
        config = {
            Irods4ServiceController._USERNAME_PARAMETER_NAME: user.username,
            Irods4ServiceController._HOST_PARAMETER_NAME: service.name,
            Irods4ServiceController._PORT_PARAMETER_NAME: Irods4ServiceController._PORT,
            Irods4ServiceController._ZONE_PARAMETER_NAME: user.zone
        }
        config_as_json = json.dumps(config)
        logging.debug("Writing iRODS connection config to: %s" % file_location)
        with open(file_location, "w") as settings_file:
            settings_file.write(config_as_json)

        return user.password

    @staticmethod
    def _start_detector(log_line: str) -> bool:
        """
        TODO
        :param log_line:
        :return:
        """
        return "iRODS server started successfully!" in log_line

    @staticmethod
    def _transient_error_detector(log_line: str) -> bool:
        """
        TODO
        :param log_line:
        :return:
        """
        # Note: iRODS schema validation has been observed to randomly fail before, raising `RuntimeError`
        return "iRODS server failed to start." in log_line or "RuntimeError:" in log_line

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
                         Irods4ServiceController._start_detector,
                         transient_error_detector=Irods4ServiceController._transient_error_detector,
                         persistent_error_detector=IrodsBaseServiceController._persistent_error_detector,
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
Irods3_3_1ServiceController = build_irods_service_controller_type(_DOCKER_REPOSITORY, "3.3.1", Irods3ServiceController)
Irods4_1_8ServiceController = build_irods_service_controller_type(_DOCKER_REPOSITORY, "4.1.8", Irods4ServiceController)
Irods4_1_9ServiceController = build_irods_service_controller_type(_DOCKER_REPOSITORY, "4.1.9", Irods4ServiceController)
Irods4_1_10ServiceController = build_irods_service_controller_type(_DOCKER_REPOSITORY, "4.1.10", Irods4ServiceController)
IrodsServiceController = Irods4_1_10ServiceController

irods_service_controllers = {Irods3_3_1ServiceController, Irods4_1_8ServiceController, Irods4_1_9ServiceController,
                             Irods4_1_10ServiceController}
