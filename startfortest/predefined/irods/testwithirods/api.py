import os
from enum import Enum
from typing import Union

from testwithirods.models import IrodsServer, IrodsUser


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
