import os
from time import sleep

from hgicommon.managers import TempManager
from useintest._common import MOUNTABLE_TEMP_DIRECTORY
from useintest.predefined.baton.executables import BatonExecutablesController
from useintest.predefined.irods import Irods4_1_10ServiceController


temp_manager = TempManager(default_mkdtemp_kwargs={"dir": MOUNTABLE_TEMP_DIRECTORY})
settings_directory = temp_manager.create_temp_directory()

irods_controller = Irods4_1_10ServiceController()
service = irods_controller.start_service()
settings = irods_controller.write_connection_settings(
    os.path.join(settings_directory, irods_controller.config_file_name), service)

try:
    controller = BatonExecutablesController(service.name, settings_directory)
    executables_directory = temp_manager.create_temp_directory()
    print(executables_directory)
    controller.write_executables_and_authenticate(service.root_user.password, executables_directory)
    sleep(1000)
finally:
    irods_controller.stop_service(service)
    temp_manager.tear_down()
