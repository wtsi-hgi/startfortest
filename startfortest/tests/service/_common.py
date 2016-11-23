from abc import ABCMeta, abstractmethod
from typing import Dict, Iterable, Type, Generic, TypeVar
from typing import Set
from unittest import TestCase

from startfortest._docker_helpers import is_docker_container_running
from startfortest.controllers import ServiceController
from startfortest.models import DockerisedService, Service
from hgicommon.docker.client import create_client

ControllerType = TypeVar("ControllerType", bound=ServiceController)


class TestDockerisedServiceControllerSubclass(Generic[ControllerType], TestCase, metaclass=ABCMeta):
    """
    Superclass for `DockerisedServiceController` tests.
    """
    @staticmethod
    @abstractmethod
    def _get_controller_type() -> ControllerType:
        """
        Gets the controller type under test.
        :return: the controller type
        """

    def setUp(self):
        self._started = set()   # type: Set[Service]
        self._docker_client = create_client()
        self.controller = type(self)._get_controller_type()()

    def test_stop(self):
        service = self._start_service()
        assert is_docker_container_running(service)
        self.controller.stop_service(service)
        self.assertFalse(is_docker_container_running(service))

    def test_stop_when_not_started(self):
        service = DockerisedService()
        self.controller.stop_service(service)

    def _start_service(self):
        service = self.controller.start_service()
        self._started.add(service)
        return service


def create_tests(superclass: Type[TestDockerisedServiceControllerSubclass], types: Iterable[type]) \
        -> Dict[str, TestCase]:
    """
    Creates tests for controller types.
    :param superclass: the test superclass (must be a subclass of `TestDockerisedServiceControllerSubclass`)
    :param types: the controller type to be tested
    :return: dictionary with the names of the tests as keys and the tests as values
    """
    tests = dict()      # type: Dict[str, TestCase]
    for test_type in types:
        name = "Test%s" % test_type.__name__
        test = type(
            name,
            (superclass[test_type],),
            {"_get_controller_type": staticmethod(lambda: test_type)}
        )
        tests[name] = test
    return tests
