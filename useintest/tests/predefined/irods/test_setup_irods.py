import unittest
from abc import ABCMeta

from hgicommon.helpers import extract_version_number
from hgicommon.testing import create_tests, get_classes_to_test, TypeUsedInTest, TestUsingType
from useintest.predefined.irods.services import irods_service_controllers, IrodsServiceController
from useintest.predefined.irods.executables import IrodsBaseExecutablesController
from useintest.predefined.irods.helpers import IrodsSetupHelper
from useintest.predefined.irods.setup_irods import setup_irods


class _TestSetupIrods(TestUsingType[TypeUsedInTest], metaclass=ABCMeta):
    """
    Tests for `setup_irods`.
    """
    def test_setup(self):
        icommands_location, service, icommands_controller, icat_controller = setup_irods(self.get_type_to_test())
        self.assertIsInstance(icommands_controller, IrodsBaseExecutablesController)
        self.assertIsInstance(icat_controller, self.get_type_to_test())
        setup_helper = IrodsSetupHelper(icommands_location)
        self.assertEqual(service.version, setup_helper.get_icat_version())


# Setup tests
globals().update(create_tests(_TestSetupIrods, get_classes_to_test(irods_service_controllers, IrodsServiceController),
                              lambda superclass, test_type: "TestSetupWith%s"
                                                            % extract_version_number(test_type.__name__).replace(".", "_")))

# Fix for stupidity of test runners
del _TestSetupIrods, TestUsingType, create_tests, get_classes_to_test

if __name__ == "__main__":
    unittest.main()
