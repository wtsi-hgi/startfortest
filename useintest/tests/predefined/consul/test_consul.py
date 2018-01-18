import unittest
from abc import ABCMeta

from consul import Consul
from hgicommon.testing import TypeUsedInTest, create_tests, get_classes_to_test

from useintest.predefined.consul.consul import ConsulServiceController, consul_service_controllers, \
    ConsulDockerisedService
from useintest.services.models import DockerisedServiceWithUsers
from useintest.tests.services.common import TestServiceControllerSubclass

_TEST_KEY = "hello"
_TEST_VALUE = "world"


class _TestConsulServiceController(
        TestServiceControllerSubclass[TypeUsedInTest, DockerisedServiceWithUsers], metaclass=ABCMeta):
    """
    Tests for `ConsulServiceController`.
    """
    def test_start(self):
        service = self._start_service()     # type: ConsulDockerisedService
        self.assertIsInstance(service, ConsulDockerisedService)
        consul_client = service.create_consul_client()
        self._test_client(consul_client)

    def test_setup_environment(self):
        service = self._start_service()     # type: ConsulDockerisedService
        service.setup_environment()
        consul_client = Consul()
        self._test_client(consul_client)

    def _test_client(self, consul_client: Consul):
        """
        Tests that the given Consul client connects to Consul
        :param consul_client: the Consul client to test
        """
        consul_client.kv.put(_TEST_KEY, _TEST_VALUE)
        self.assertEqual(_TEST_VALUE, consul_client.kv.get(_TEST_KEY)[1]["Value"].decode("utf-8"))


# Setup tests
globals().update(create_tests(_TestConsulServiceController, get_classes_to_test(
    consul_service_controllers, ConsulServiceController)))

# Fix for stupidity of test runners
del _TestConsulServiceController, TestServiceControllerSubclass, create_tests, get_classes_to_test

if __name__ == "__main__":
    unittest.main()
