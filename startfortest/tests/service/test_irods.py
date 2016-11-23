import shutil
import unittest
from abc import ABCMeta

from startfortest.service.irods import Irods4_1_10Controller
from startfortest.tests.service._common import TestDockerisedServiceControllerSubclass, create_tests, ControllerType
from testwithirods.helpers import SetupHelper
from testwithirods.proxies import ICommandProxyController


class _TestIrodsServiceController(TestDockerisedServiceControllerSubclass[ControllerType], metaclass=ABCMeta):
    """
    Tests for iRODS controller.
    """
    def test_start(self):
        service = self._start_service()
        proxy_controller = ICommandProxyController(service, "mercury/icat:%s" % service.version)
        icommands_location = None
        try:
            icommands_location = proxy_controller.create_proxy_binaries()
            setup_helper = SetupHelper(icommands_location)
            name, data = "name", "data"
            data_object_path = setup_helper.create_data_object(name, data)
            self.assertEqual(data, setup_helper.read_data_object(data_object_path))
        finally:
            shutil.rmtree(icommands_location)


# Setup tests
CLASSES_TO_TEST = {Irods4_1_10Controller}
globals().update(create_tests(_TestIrodsServiceController, CLASSES_TO_TEST))


# Fix for unittest
del _TestIrodsServiceController
del TestDockerisedServiceControllerSubclass


if __name__ == "__main__":
    unittest.main()
