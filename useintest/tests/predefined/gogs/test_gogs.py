import unittest
from abc import ABCMeta

from gogs_client import UsernamePassword, GogsApi
from hgicommon.testing import TypeUsedInTest, create_tests, get_classes_to_test

from useintest.predefined.gogs.gogs import gogs_service_controllers, GogsServiceController
from useintest.services.models import DockerisedServiceWithUsers
from useintest.tests.services.common import TestServiceControllerSubclass

_REPO_NAME = "test"


class _TestGogsBaseServiceController(
    TestServiceControllerSubclass[TypeUsedInTest, DockerisedServiceWithUsers], metaclass=ABCMeta):
    """
    Tests for `GogsBaseServiceController`.
    """
    def test_start(self):
        service = self._start_service()

        authentication = UsernamePassword(service.root_user.username, service.root_user.password)
        gogs_connection = GogsApi(f"http://{service.host}:{service.ports[3000]}")
        gogs_connection.create_repo(authentication, _REPO_NAME)

        self.assertEqual(f"{authentication.username}/{_REPO_NAME}",
                          gogs_connection.get_repo(authentication, authentication.username, _REPO_NAME).full_name)


# Setup tests
globals().update(create_tests(_TestGogsBaseServiceController, get_classes_to_test(
    gogs_service_controllers, GogsServiceController)))

# Fix for stupidity of test runners
del _TestGogsBaseServiceController, TestServiceControllerSubclass, create_tests, get_classes_to_test

if __name__ == "__main__":
    unittest.main()
