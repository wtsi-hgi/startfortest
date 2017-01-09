import os
import shutil
import unittest
from abc import ABCMeta
from tempfile import TemporaryDirectory

from hgicommon.testing import TypeToTest, create_tests, get_classes_to_test
from startfortest.predefined.irods import IrodsExecutablesController
from startfortest.predefined.irods.helpers import SetupHelper
from startfortest.predefined.irods.services import irods_service_controllers, IrodsServiceController
from startfortest.tests.common import MOUNTABLE_TEMP_DIRECTORY
from startfortest.tests.service.common import TestDockerisedServiceControllerSubclass


class _TestIrodsServiceController(TestDockerisedServiceControllerSubclass[TypeToTest], metaclass=ABCMeta):
    """
    Tests for iRODS controller.
    """
    def test_start(self):
        with TemporaryDirectory(dir=MOUNTABLE_TEMP_DIRECTORY) as settings_directory:
            service = self._start_service()

            config_file_path = os.path.join(settings_directory, self.icat_controller.config_file_name)
            password = self.get_type_to_test().write_connection_settings(config_file_path, service)

            # TODO: Docker repo+tag should be a setting
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
globals().update(create_tests(_TestIrodsServiceController, get_classes_to_test(irods_service_controllers, IrodsServiceController)))


# Fix for stupidity of test runners
del _TestIrodsServiceController, TestDockerisedServiceControllerSubclass, create_tests, get_classes_to_test

if __name__ == "__main__":
    unittest.main()
