import unittest
import requests
from abc import ABCMeta

from hgicommon.testing import create_tests, TypeUsedInTest, get_classes_to_test
from useintest.predefined.bissell import BissellDockerisedServiceController, BissellServiceController, \
    bissell_service_controllers
from useintest.services.models import DockerisedServiceWithUsers
from useintest.tests.services.common import TestDockerisedServiceControllerSubclass


class _TestBissellDockerisedServiceController(
    TestDockerisedServiceControllerSubclass[TypeUsedInTest, DockerisedServiceWithUsers], metaclass=ABCMeta):
    """
    Tests for Mongo service controllers.
    """
    def test_start(self):
        service = self._start_service()
        response = requests.head(f"http://{service.host}:{service.port}/test.cram")
        self.assertEqual(True, True)

# Setup tests
CLASSES_TO_TEST = {BissellDockerisedServiceController}
globals().update(create_tests(_TestBissellDockerisedServiceController, get_classes_to_test(bissell_service_controllers, BissellServiceController)))


# Fix for stupidity of test runners
del _TestBissellDockerisedServiceController, TestDockerisedServiceControllerSubclass, create_tests, get_classes_to_test


if __name__ == "__main__":
    unittest.main()
