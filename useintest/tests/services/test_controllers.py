import unittest

import docker
from docker.errors import NotFound

from useintest.services._builders import DockerisedServiceControllerTypeBuilder


NoopServiceController = DockerisedServiceControllerTypeBuilder(
    name="NoopController",
    repository="ubuntu",
    ports=[],
    tag="xenial",
    additional_run_settings={"entrypoint": "tail", "command": ["-f", "/etc/hosts"]},
    start_detector=lambda log_line: log_line.strip() != "",
).build()


class TestDockerisedServiceController(unittest.TestCase):
    """
    Tests for `DockerisedServiceController`.
    """
    def setUp(self):
        self._docker_client = docker.from_env()
        self._service_controller = NoopServiceController()

    def test_context_manager(self):
        with self._service_controller.start_service() as service:
            self.assertEqual("running", self._docker_client.containers.get(service.container["Id"]).status)
        self.assertRaises(NotFound,  self._docker_client.containers.get, service.container["Id"])

    def test_context_manager_exit_when_service_stopped(self):
        with self._service_controller.start_service() as service:
            self._service_controller.stop_service(service)
