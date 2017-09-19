import json
import unittest
from abc import ABCMeta

import requests

from hgicommon.testing import TypeUsedInTest, create_tests, get_classes_to_test
from useintest.predefined.gitlab.gitlab import GitLabServiceController, gitlab_service_controllers
from useintest.services.models import DockerisedServiceWithUsers
from useintest.tests.services.common import TestServiceControllerSubclass


class _TestGitLabBaseServiceController(
    TestServiceControllerSubclass[TypeUsedInTest, DockerisedServiceWithUsers], metaclass=ABCMeta):
    """
    Tests for `GitLabBaseServiceController`.
    """
    def test_start(self):
        service = self._start_service()
        response = requests.post(f"http://localhost:{service.ports[80]}/api/v3/session", data={
            "login": service.root_user.username, "password": service.root_user.password})
        print(response.text)
        response_payload = json.loads(response.text)
        self.assertEqual(service.root_user.username, response_payload["username"])


# Setup tests
globals().update(create_tests(_TestGitLabBaseServiceController, get_classes_to_test(
    gitlab_service_controllers, GitLabServiceController)))

# Fix for stupidity of test runners
del _TestGitLabBaseServiceController, TestServiceControllerSubclass, create_tests, get_classes_to_test

if __name__ == "__main__":
    unittest.main()
