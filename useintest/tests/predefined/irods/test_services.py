import os
import shutil
import unittest
from abc import ABCMeta
from tempfile import TemporaryDirectory

from hgicommon.helpers import extract_version_number
from hgicommon.testing import TypeToTest, create_tests, get_classes_to_test
from useintest.predefined.irods.executables import irods_executables_controllers_and_versions
from useintest.predefined.irods.helpers import IrodsSetupHelper
from useintest.predefined.irods.models import Version
from useintest.predefined.irods.services import irods_service_controllers, IrodsServiceController
from useintest._common import MOUNTABLE_TEMP_DIRECTORY
from useintest.tests.service.common import TestDockerisedServiceControllerSubclass


class _TestIrodsServiceController(TestDockerisedServiceControllerSubclass[TypeToTest], metaclass=ABCMeta):
    """
    Tests for iRODS controller.
    """
    def setUp(self):
        super().setUp()
        self.irods_version = Version(extract_version_number(self.get_type_to_test().__name__))

    def test_start(self):
        with TemporaryDirectory(dir=MOUNTABLE_TEMP_DIRECTORY) as settings_directory:
            service = self._start_service()

            config_file_path = os.path.join(settings_directory, self.service_controller.config_file_name)
            password = self.get_type_to_test().write_connection_settings(config_file_path, service)

            ExecutablesController = irods_executables_controllers_and_versions[service.version]
            irods_executables_controller = ExecutablesController(service.name, settings_directory)

            icommands_location = None
            try:
                icommands_location = irods_executables_controller.write_executables_and_authenticate(password)
                setup_helper = IrodsSetupHelper(icommands_location)

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
