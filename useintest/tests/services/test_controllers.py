import unittest

from docker.errors import NotFound

from useintest.common import docker_client
from useintest.services.builders import DockerisedServiceControllerTypeBuilder
from useintest.services.exceptions import ServiceStartError

NoopServiceController = DockerisedServiceControllerTypeBuilder(
    name="NoopController",
    repository="alpine",
    ports=[],
    tag="3.6",
    additional_run_settings={"entrypoint": "tail", "command": ["-f", "/etc/hosts"]},
    start_log_detector=lambda log_line: log_line.strip() != "",
).build()


class TestDockerisedServiceController(unittest.TestCase):
    """
    Tests for `DockerisedServiceController`.
    """
    def setUp(self):
        self._service_controller = NoopServiceController()

    def test_context_manager(self):
        with self._service_controller.start_service() as service:
            self.assertEqual("running", service.container.status)
            container_id = service.container_id
        self.assertIsNone(service.container)
        self.assertRaises(NotFound, docker_client.containers.get, container_id)

    def test_context_manager_exit_when_service_stopped(self):
        with self._service_controller.start_service() as service:
            self._service_controller.stop_service(service)
            self.assertIsNone(service.container)

    def test_service_stopped_on_start_detection(self):
        ExitingController = DockerisedServiceControllerTypeBuilder(
            name="ExitingController",
            repository="alpine",
            ports=[],
            tag="3.6",
            start_log_detector=lambda line: False,
            start_tries=1
        ).build()
        self.assertRaises(ServiceStartError, ExitingController().start_service)
