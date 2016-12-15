import os
import shutil
import unittest
from abc import ABCMeta
from tempfile import TemporaryDirectory

from startfortest.predefined.irods import IrodsExecutablesController
from startfortest.predefined.irods.services import Irods3_3_1ServiceController, Irods4_1_8ServiceController, \
    Irods4_1_9ServiceController, Irods4_1_10ServiceController
from startfortest.predefined.irods.testwithirods.helpers import SetupHelper
from startfortest.tests.service.common import TestDockerisedServiceControllerSubclass, ControllerType, create_tests
from testwithirods.helpers import SetupHelper


class _TestIrodsServiceController(TestDockerisedServiceControllerSubclass[ControllerType], metaclass=ABCMeta):
    """
    Tests for iRODS controller.
    """
    def test_start(self):
        # TODO: `/tmp` is not very cross-platform!
        with TemporaryDirectory(dir="/tmp") as settings_directory:
            service = self._start_service()

            config_file_path = os.path.join(settings_directory, self.controller.config_file_name)
            password = self._get_controller_type().write_connection_settings(config_file_path, service)

            irods_executables_controller = IrodsExecutablesController(
                service.name, "mercury/icat:%s" % service.version, settings_directory)

            icommands_location = None
            try:
                icommands_location = irods_executables_controller.write_executables_and_authenticate(password)
                setup_helper = SetupHelper(icommands_location)

                # TODO: This is really 2 tests - one checking the version, one checking the file upload/download
                self.assertEqual(service.version, setup_helper.get_icat_version())
                name, data = "name", "data"
                data_object_path = setup_helper.create_data_object(name, data)
                self.assertEqual(data, setup_helper.read_data_object(data_object_path))
            finally:
                if icommands_location is not None:
                    shutil.rmtree(icommands_location)
                irods_executables_controller.tear_down()


# Setup tests
CLASSES_TO_TEST = {
    Irods3_3_1ServiceController,
    Irods4_1_8ServiceController,
    Irods4_1_9ServiceController,
    Irods4_1_10ServiceController}
globals().update(create_tests(_TestIrodsServiceController, CLASSES_TO_TEST))


# Fix for unittest
del _TestIrodsServiceController
del TestDockerisedServiceControllerSubclass


if __name__ == "__main__":
    unittest.main()
