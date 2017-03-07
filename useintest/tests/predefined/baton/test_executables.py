import json
import logging
import os
import subprocess
import unittest
from abc import ABCMeta

from hgicommon.managers import TempManager
from hgicommon.testing import create_tests, TestUsingType, TypeUsedInTest, get_classes_to_test
from useintest._common import MOUNTABLE_TEMP_DIRECTORY
from useintest.predefined.baton.executables import baton_executables_controllers, BatonExecutablesController
from useintest.predefined.irods import IrodsSetupHelper, irods_executables_controllers_and_versions
from useintest.predefined.irods.services import irods_service_controllers_and_versions


class _TestBatonExecutablesController(TestUsingType[TypeUsedInTest], metaclass=ABCMeta):
    """
    Tests for executables controllers for baton.
    """
    def setUp(self):
        self.irods_controller = irods_service_controllers_and_versions[self.get_type_to_test().irods_version]()
        self.irods_service = self.irods_controller.start_service()

        self.temp_manager = TempManager(default_mkdtemp_kwargs={"dir": MOUNTABLE_TEMP_DIRECTORY})
        settings_directory = self.temp_manager.create_temp_directory()
        self.irods_controller.write_connection_settings(
            os.path.join(settings_directory, self.irods_controller.config_file_name), self.irods_service)

        self.irods_executables_controller = irods_executables_controllers_and_versions[
            self.get_type_to_test().irods_version](self.irods_service.name, settings_directory)

        self.controller = self.get_type_to_test()(self.irods_service.name, settings_directory)
        self.executables_location = self.controller.write_executables()

    def test_can_use_baton(self):
        process = subprocess.Popen([os.path.join(self.executables_location, "baton")], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        out, error = process.communicate()

        self.assertEqual(str.strip(out.decode("utf-8")), "{\"avus\":[]}")
        self.assertEqual(error, b"")

    def test_can_use_baton_list(self):
        self.controller.authenticate(self.irods_service.root_user.password)
        test_data_object_name = "test"

        setup_helper = self._create_setup_helper()
        data_object_location = setup_helper.create_data_object(test_data_object_name)
        collection, data_object = data_object_location.rsplit("/", 1)
        baton_location_representation = {"collection": collection, "data_object": data_object}

        process = subprocess.Popen([os.path.join(self.executables_location, "baton-list")], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        out, error = process.communicate(input=str.encode(json.dumps(baton_location_representation)))

        self.assertEqual(json.loads(str.strip(out.decode("utf-8"))), baton_location_representation)
        self.assertEqual(error, b"")

    def tearDown(self):
        try:
            self.irods_controller.stop_service(self.irods_service)
        except Exception as e:
            logging.error(e)
        self.temp_manager.tear_down()
        self.irods_executables_controller.tear_down()
        self.controller.tear_down()

    def _create_setup_helper(self) -> IrodsSetupHelper:
        """
        TODO
        :return: 
        """
        icommands_location = self.irods_executables_controller.write_executables_and_authenticate(
            self.irods_service.root_user.password)
        return IrodsSetupHelper(icommands_location)


# Setup tests
globals().update(create_tests(_TestBatonExecutablesController,
                              get_classes_to_test(baton_executables_controllers, BatonExecutablesController)))

# Fix for stupidity of test runners
del _TestBatonExecutablesController, TestUsingType, create_tests


if __name__ == "__main__":
    unittest.main()
