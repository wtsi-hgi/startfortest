from abc import ABCMeta
from typing import Set
from unittest import TestCase

from hgicommon.docker.client import create_client
from hgicommon.testing import TestUsingType, TypeToTest
from startfortest._docker_helpers import is_docker_container_running
from startfortest.services.models import DockerisedService, Service


class TestServiceControllerSubclass(TestUsingType[TypeToTest], TestCase, metaclass=ABCMeta):
    """
    TODO
    """
    def setUp(self):
        self._started = set()   # type: Set[Service]
        self._docker_client = create_client()
        self.icat_controller = type(self).get_type_to_test()()

    def tearDown(self):
        for service in self._started:
            self.icat_controller.stop_service(service)

    def _start_service(self) -> Service:
        service = self.icat_controller.start_service()
        self._started.add(service)
        return service


class TestDockerisedServiceControllerSubclass(TestServiceControllerSubclass[TypeToTest], metaclass=ABCMeta):
    """
    Superclass for `DockerisedServiceController` tests.
    """
    def test_stop(self):
        service = self._start_service()
        assert is_docker_container_running(service)
        self.icat_controller.stop_service(service)
        self.assertFalse(is_docker_container_running(service))

    def test_stop_when_not_started(self):
        service = DockerisedService()
        self.icat_controller.stop_service(service)
