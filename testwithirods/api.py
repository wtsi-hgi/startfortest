import os
from enum import Enum, unique
from typing import Union

from testwithirods.irods_3_controller import StaticIrods3_3_1ServerController
from testwithirods.irods_4_controller import StaticIrods4_1_8ServerController
from testwithirods.irods_4_controller import StaticIrods4_1_9ServerController
from testwithirods.irods_contoller import StaticIrodsServerController
from testwithirods.models import IrodsServer, IrodsUser


@unique
class IrodsVersion(Enum):
    """
    Enum mapping between iRODS server versions and the related server controllers.
    """
    v3_3_1 = StaticIrods3_3_1ServerController
    v4_1_8 = StaticIrods4_1_8ServerController
    v4_1_9 = StaticIrods4_1_9ServerController


def get_static_irods_server_controller(irods_version: IrodsVersion=IrodsVersion.v4_1_9) -> StaticIrodsServerController:
    """
    Gets a controller for the an iRODS server of the given version.
    :param irods_version: the iRODS version that the controller must work with
    :return: the iRODS server controller
    """
    return irods_version.value


class IrodsEnvironmentKey(Enum):
    """
    Keys of environment variables that may be used to define an iRODS server that can be loaded using
    `get_irods_server_from_environment_if_defined`.
    """
    IRODS_HOST = "IRODS_HOST"
    IRODS_PORT = "IRODS_PORT"
    IRODS_USERNAME = "IRODS_USERNAME"
    IRODS_PASSWORD = "IRODS_PASSWORD"
    IRODS_ZONE = "IRODS_ZONE"


def get_irods_server_from_environment_if_defined() -> Union[None, IrodsServer]:
    """
    Instantiates an iRODS server that has been defined through environment variables. If no definition/an incomplete
    definition was found, returns `None`.
    :return: a representation of the iRODS server defined through environment variables else `None` if no definition
    """
    for key in IrodsEnvironmentKey:
        environment_value = os.environ.get(key.value)
        if environment_value is None:
            return None

    return IrodsServer(
        os.environ[IrodsEnvironmentKey.IRODS_HOST.value],
        int(os.environ[IrodsEnvironmentKey.IRODS_PORT.value]),
        [IrodsUser(os.environ[IrodsEnvironmentKey.IRODS_USERNAME.value],
                   os.environ[IrodsEnvironmentKey.IRODS_ZONE.value],
                   os.environ[IrodsEnvironmentKey.IRODS_PASSWORD.value])]
    )
