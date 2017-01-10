import os
from typing import Tuple, Type

from hgicommon.managers import TempManager
from useintest._common import MOUNTABLE_TEMP_DIRECTORY
from useintest.predefined.irods.services import IrodsServiceController, IrodsBaseServiceController
from useintest.predefined.irods.executables import IrodsExecutablesController, \
    irods_executables_controllers_and_versions
from useintest.predefined.irods.models import IrodsDockerisedService

_temp_manager = TempManager()


def setup_irods(irods_service_controller: Type[IrodsBaseServiceController]=IrodsServiceController) \
        -> Tuple[str, IrodsDockerisedService, IrodsExecutablesController, IrodsBaseServiceController]:
    """
    Sets up an iRODS server and the icommands needed to access the server from the local machine.
    :param irods_service_controller:
    :return: tuple where the first item is the location of the icommands on the host, the second is the iCAT service,
    the thirds is the controller for the icommand executables and the last is the controller for the iCAT service
    """
    global _temp_manager

    # Setup iRODS server
    icat_controller = irods_service_controller()
    service = icat_controller.start_service()

    # Write iRODS connection settings for the server
    settings_directory = _temp_manager.create_temp_directory(dir=MOUNTABLE_TEMP_DIRECTORY)
    config_file = os.path.join(settings_directory, icat_controller.config_file_name)
    password = irods_service_controller.write_connection_settings(config_file, service)

    # Setup iRODS executables
    ExecutablesController = irods_executables_controllers_and_versions[service.version]
    icommands_controller = ExecutablesController(service.name, settings_directory)
    icommands_location = icommands_controller.write_executables_and_authenticate(password)

    return icommands_location, service, icommands_controller, icat_controller
