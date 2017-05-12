import unittest
from abc import ABCMeta

from hgicommon.testing import TypeUsedInTest, create_tests, get_classes_to_test
from useintest.predefined.irods.setup_irods import setup_irods
from useintest.predefined.irods.helpers import IrodsSetupHelper
from useintest.predefined.irods.services import irods_service_controllers, IrodsServiceController
from useintest.services.models import DockerisedServiceWithUsers
from useintest.tests.services.common import TestDockerisedServiceControllerSubclass


class _TestIrodsServiceController(
    TestDockerisedServiceControllerSubclass[TypeUsedInTest, DockerisedServiceWithUsers], metaclass=ABCMeta):
    """
    Tests for iRODS controller.
    """
    def setUp(self):
        super().setUp()
        self.icommands_location, self.service, self.icommands_controller, self.icat_controller = setup_irods(
            irods_service_controller=self.get_type_to_test())
        self.setup_helper = IrodsSetupHelper(self.icommands_location)

    def tearDown(self):
        super().tearDown()
        self.icat_controller.stop_service(self.service)
        self.icommands_controller.tear_down()

    def test_starts(self):
        name, data = "name", "data"
        data_object_path = self.setup_helper.create_data_object(name, data)
        self.assertEqual(data, self.setup_helper.read_data_object(data_object_path))

    def test_starts_correct_version(self):
        setup_helper = IrodsSetupHelper(self.icommands_location)
        self.assertEqual(self.service.version, self.setup_helper.get_icat_version())


# Setup tests
globals().update(create_tests(_TestIrodsServiceController, get_classes_to_test(irods_service_controllers, IrodsServiceController)))

# Fix for stupidity of test runners
del _TestIrodsServiceController, TestDockerisedServiceControllerSubclass, create_tests, get_classes_to_test

if __name__ == "__main__":
    unittest.main()
