from abc import ABCMeta, abstractmethod
from typing import Dict, Iterable
from unittest import TestCase

from startfortest.models import Container
from hgicommon.docker.client import create_client


class TestDockerControllerSubclass(TestCase, metaclass=ABCMeta):
    """
    Superclass for `DockerController` tests.
    """
    @staticmethod
    @abstractmethod
    def _get_controller_type() -> type:
        """
        Gets the controller type under test.
        :return: the controller type
        """

    def setUp(self):
        self._docker_client = create_client()

    def test_stop(self):
        controller = type(self)._get_controller_type()()
        container = controller.start_service()
        assert self._docker_client.inspect_container(container.native_object)["State"]["Status"] == "running"
        controller.stop_service(container)
        self.assertEqual("exited", self._docker_client.inspect_container(container.native_object)["State"]["Status"])

    def test_stop_when_not_started(self):
        controller = type(self)._get_controller_type()()
        container = Container()
        controller.stop_service(container)


def create_tests(superclass: type, types: Iterable[type]) -> Dict[str, TestCase]:
    """
    Creates tests for controller types.
    :param superclass: the test superclass (must be a subclass of `TestDockerControllerSubclass`)
    :param types: the controller type to be tested
    :return: dictionary with the names of the tests as keys and the tests as values
    """
    tests = dict()      # type: Dict[str, TestCase]
    for test_type in types:
        name = "Test%s" % test_type.__name__
        test = type(
            name,
            (superclass,),
            {"_get_controller_type": staticmethod(lambda: test_type)}
        )
        tests[name] = test
    return tests
