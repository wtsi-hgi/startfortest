import unittest
from abc import ABCMeta, abstractmethod
from typing import Dict
from unittest import TestCase

from bringupfortest.models import Container
from hgicommon.docker.client import create_client


class TestDockerControllerSubclass(TestCase, metaclass=ABCMeta):
    """
    TODO
    """
    @staticmethod
    @abstractmethod
    def _get_controller_type() -> type:
        """
        TODO
        :return:
        """

    def setUp(self):
        self._docker_client = create_client()

    def test_stop(self):
        controller = type(self)._get_controller_type()()
        container = controller.start()
        assert self._docker_client.inspect_container(container.native_object)["State"]["Status"] == "running"
        controller.stop(container)
        self.assertEqual("exited", self._docker_client.inspect_container(container.native_object)["State"]["Status"])

    def test_stop_when_not_started(self):
        controller = type(self)._get_controller_type()()
        container = Container()
        controller.stop(container)


def create_tests(superclass, types) -> Dict[str, TestCase]:
    """
    TODO
    :param superclass:
    :param types:
    :return:
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
