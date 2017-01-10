import unittest

from hgicommon.helpers import extract_version_number
from hgicommon.testing import create_tests, get_classes_to_test, TypeToTest, TestUsingType
from useintest.predefined.irods import irods_service_controllers, IrodsServiceController, ABCMeta, \
    IrodsBaseExecutablesController, IrodsSetupHelper
from useintest.predefined.irods.setup import setup


class _TestSetup(TestUsingType[TypeToTest], metaclass=ABCMeta):
    """
    Tests for `setup`.
    """
    def test_setup(self):
        icommands_location, service, icommands_controller, icat_controller = setup(self.get_type_to_test())
        self.assertIsInstance(icommands_controller, IrodsBaseExecutablesController)
        self.assertIsInstance(icat_controller, self.get_type_to_test())
        setup_helper = IrodsSetupHelper(icommands_location)
        self.assertEqual(service.version, setup_helper.get_icat_version())


# Setup tests
globals().update(create_tests(_TestSetup, get_classes_to_test(irods_service_controllers, IrodsServiceController),
                              lambda superclass, test_type: "TestSetupWith%s"
                                                            % extract_version_number(test_type.__name__).replace(".", "_")))

# Fix for stupidity of test runners
del _TestSetup, TestUsingType, create_tests, get_classes_to_test

if __name__ == "__main__":
    unittest.main()
