from abc import ABCMeta
from typing import Set, Generic, TypeVar
from unittest import TestCase

from testhelpers import TypeUsedInTest, TestUsingType

from useintest.common import docker_client
from useintest.services.models import DockerisedService, Service

ServiceType = TypeVar("ServiceType", bound=Service)


# TODO: These need sorting out - why is there 2 classes here?
class TestServiceControllerSubclass(Generic[TypeUsedInTest, ServiceType], TestUsingType[TypeUsedInTest], TestCase,
                                    metaclass=ABCMeta):
    """
    TODO
    """
    def setUp(self):
        super().setUp()
        self._started: Set[ServiceType] = set()
        self.service_controller = type(self).get_type_to_test()()

    def tearDown(self):
        for service in self._started:
            self.service_controller.stop_service(service)

    def _start_service(self) -> ServiceType:
        service = self.service_controller.start_service()
        self._started.add(service)
        return service


class TestDockerisedServiceControllerSubclass(Generic[TypeUsedInTest, ServiceType],
                                              TestServiceControllerSubclass[TypeUsedInTest, ServiceType],
                                              metaclass=ABCMeta):
    """
    Superclass for `DockerisedServiceController` tests.
    """
    def test_stop(self):
        service = self._start_service()
        assert len(docker_client.containers.list(filters=dict(name=service.name))) == 1
        self.service_controller.stop_service(service)
        self.assertEqual(0, len(docker_client.containers.list(filters=dict(name=service.name))))

    def test_stop_when_not_started(self):
        service = DockerisedService()
        self.service_controller.stop_service(service)
