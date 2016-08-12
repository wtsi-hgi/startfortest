import unittest
from abc import ABCMeta

import testwithicat
from hgicommon.docker.client import create_client
from testwithicat.helpers import SetupHelper
from testwithicat.irods_contoller import IrodsServerController
from testwithicat.models import ContainerisedIrodsServer
from testwithicat.proxies import ICommandProxyController
from testwithicat.tests._common import create_tests_for_all_icat_setups, IcatTest


class TestIrodsServerController(IcatTest, metaclass=ABCMeta):
    """
    Tests for `IrodsServerController`.
    """
    @staticmethod
    def _is_container_running(container: ContainerisedIrodsServer) -> bool:
        """
        Gets whether the given container is running. Will raise an exception if the container does not exist.
        :param container: the container
        :return: whether the container is running
        """
        docker_client = create_client()
        return docker_client.inspect_container(container.native_object)["State"]["Running"]

    def setUp(self):
        self.irods_controller = self.ServerController()     # type: IrodsServerController

    def test_start_server(self):
        irods_server = self.irods_controller.start_server()
        self.assertTrue(self._is_container_running(irods_server))

        repository, tag = self.compatible_baton_image.split(":")
        create_client().pull(repository, tag)

        proxy_controller = ICommandProxyController(irods_server, self.compatible_baton_image)
        icommand_binaries_location = proxy_controller.create_proxy_binaries()
        setup_helper = SetupHelper(icommand_binaries_location)

        self.assertEqual(setup_helper.get_icat_version(), self.ServerController.VERSION)

    def test_stop_server(self):
        irods_container = self.irods_controller.start_server()
        assert self._is_container_running(irods_container)
        self.irods_controller.stop_server(irods_container)
        self.assertFalse(self._is_container_running(irods_container))


# Setup tests for all iCAT setups
create_tests_for_all_icat_setups(TestIrodsServerController)
for name, value in testwithicat.tests._common.__dict__.items():
    if TestIrodsServerController.__name__ in name:
        globals()[name] = value
del TestIrodsServerController


if __name__ == "__main__":
    unittest.main()
