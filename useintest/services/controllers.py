import atexit
import logging
import math
import socket
from abc import ABCMeta, abstractmethod
from inspect import signature
from typing import Dict, Iterator, List, Callable, TypeVar, Generic, Type
from uuid import uuid4

from docker.errors import NotFound
from stopit import ThreadingTimeout, TimeoutException

from useintest.executables.common import pull_docker_image
from useintest.common import docker_client
from useintest.services.exceptions import ServiceStartError, TransientServiceStartError, \
    PersistentServiceStartError
from useintest.services.models import Service, DockerisedService, DockerisedServiceWithUsers

_logger = logging.getLogger(__name__)

ServiceType = TypeVar("ServiceType", bound=Service)
DockerisedServiceType = TypeVar("DockerisedServiceType", bound=DockerisedService)
DockerisedServiceWithUsersType = TypeVar("DockerisedServiceWithUsersType", bound=DockerisedServiceWithUsers)


def _get_open_port() -> int:
    """
    Gets a PORT that will (probably) be available on the machine.
    It is possible that in-between the time in which the open PORT of found and when it is used, another process may
    bind to it instead.
    :return: the (probably) available PORT
    """
    free_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    free_socket.bind(("", 0))
    free_socket.listen(1)
    port = free_socket.getsockname()[1]
    free_socket.close()
    return port


class ServiceController(Generic[ServiceType], metaclass=ABCMeta):
    """
    Service controller.
    """
    def __init__(self, service_model: Type[ServiceType]):
        """
        Constructor.
        :param service_model: the type of model for the service this controller handles
        """
        # XXX: It would nice to do `ServiceModel()` but I don't think this is possible in Python
        self._service_model = service_model

    @abstractmethod
    def start_service(self) -> ServiceType:
        """
        Starts a service.
        :raises ServiceStartException: service could not be started (see logs for more information)
        :return: model of the started service
        """

    @abstractmethod
    def stop_service(self, service: ServiceType):
        """
        Stops the given service.
        :param service: model of the service to stop
        """


class ContainerisedServiceController(Generic[ServiceType], ServiceController[ServiceType], metaclass=ABCMeta):
    """
    Controller of containers running a service brought up for testing.
    """
    @abstractmethod
    def _start(self, service: Service):
        """
        Starts a container.
        :param service: model of the service to start
        """

    @abstractmethod
    def _stop(self, service: Service):
        """
        Stops the given container.
        :param service: model of the service to stop
        """

    @abstractmethod
    def _wait_until_started(self, service: Service) -> bool:
        """
        Blocks until the given container has started.
        :raises ServiceStartException: raised if service cannot be started
        :param service: the service
        :return: `True` if the service has started successfully
        """

    def __init__(self, service_model: Type[ServiceType], start_timeout: float=math.inf, start_tries: int=10,
                 stop_on_exit: bool=True):
        """
        Constructor.
        :param stop_on_exit: see `Container.__init__`
        :param start_timeout: timeout before for container start
        :param start_tries: number of times to try to start the container before giving up (will only try once if a
        `PersistentServiceStartException` is raised
        :param stop_on_exit: whether to stop all started containers on exit
        """
        super().__init__(service_model)
        self.start_timeout = start_timeout
        self.start_tries = start_tries
        self.stop_on_exit = stop_on_exit

    def start_service(self) -> ServiceType:
        service = self._service_model()
        assert service is not None
        if self.stop_on_exit:
            atexit.register(self.stop_service, service)

        started = False
        tries = 0
        while not started:
            if tries >= self.start_tries:
                raise ServiceStartError()
            if tries > 0:
                self._stop(service)
            self._start(service)
            try:
                if self.start_timeout is not math.inf:
                    with ThreadingTimeout(self.start_timeout, swallow_exc=False):
                        started = self._wait_until_started(service)
                else:
                    started = self._wait_until_started(service)
            except TimeoutException as e:
                _logger.warning(e)
            except TransientServiceStartError as e:
                _logger.warning(e)

            tries += 1
        return service

    def stop_service(self, service: ServiceType):
        self._stop(service)


class DockerisedServiceController(
        Generic[DockerisedServiceType], ContainerisedServiceController[DockerisedServiceType], metaclass=ABCMeta):
    """
    Controller of Docker containers running a service brought up for testing.
    """
    @staticmethod
    def _call_detector_with_correct_arguments(detector: Callable, line: str, service: DockerisedServiceType) \
            -> bool:
        """
        Calls the given detector with either line as the only argument or both line and service, depending on the
        detector's signature.
        :param detector: the detector to call
        :param line: the log line to give to the detector
        :param service: the service being started
        :return: the detector's return value
        """
        number_of_parameters = len(signature(detector).parameters)
        if number_of_parameters == 1:
            return detector(line)
        else:
            return detector(line, service)

    def __init__(self, service_model: Type[ServiceType], repository: str, tag: str, ports: List[int],
                 start_detector: Callable[..., bool]=None,
                 persistent_error_detector: Callable[..., bool]=None,
                 transient_error_detector: Callable[..., bool]=None,
                 start_timeout: int=math.inf, start_tries: int=math.inf, additional_run_settings: dict=None,
                 startup_monitor: Callable[[DockerisedServiceType], bool]=None):
        """
        Constructor.
        :param service_model: see `ServiceController.__init__`
        :param repository: the Dockerhub repository of the service to start
        :param tag: the Dockerhub repository tag of the service to start
        :param ports: the ports the service exposes
        :param start_detector: function that detects if the service is ready to use from the logs
        :param persistent_error_detector: function that detects if the service is unable to start
        :param transient_error_detector: function that detects if the service encountered a transient error when
        starting
        :param start_timeout: timeout for starting containers
        :param start_tries: number of times to try starting the containerised service
        :param additional_run_settings: other run settings (see https://docker-py.readthedocs.io/en/1.2.3/api/#create_container)
        :param startup_monitor: override the default, log based code that waits for the service to start, with a custom
        monitor that should return `True` when the service has started or raise an exception if it is not going to start
        """
        super().__init__(service_model, start_timeout, start_tries)
        self.repository = repository
        self.tag = tag
        self.ports = ports
        self.start_detector = start_detector
        self.persistent_error_detector = persistent_error_detector
        self.transient_error_detector = transient_error_detector
        self.run_settings = additional_run_settings if additional_run_settings is not None else {}
        self.startup_monitor = startup_monitor
        self._log_iterator: Dict[Service, Iterator] = dict()

    def _start(self, service: DockerisedServiceType):
        pull_docker_image(self.repository, self.tag)
        image = docker_client.images.pull(self.repository, tag=self.tag)

        service.name = f"{self.repository.split('/')[-1]}-{uuid4()}"
        service.ports = {port: _get_open_port() for port in self.ports}
        service.controller = self

        container = docker_client.containers.create(
            image=image.id,
            name=service.name,
            ports=service.ports,
            detach=True,
            **self.run_settings)
        service.container = container

        container.start()

    def _stop(self, service: DockerisedServiceType):
        if service in self._log_iterator:
            del self._log_iterator[service]
        if service.container:
            try:
                service.container.stop()
                service.container.remove(force=True)
            except NotFound:
                pass

    def _wait_until_started(self, service: DockerisedServiceType) -> bool:
        if self.startup_monitor is not None:
            return self.startup_monitor(service)
        else:
            log_stream = service.container.logs(stream=True)
            for line in log_stream:
                # XXX: Although non-streamed logs are returned as a string, the generator returns bytes!?
                # http://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.Container.logs
                line = line.decode("utf-8")
                logging.debug(line)

                if self.persistent_error_detector is not None \
                        and self._call_detector_with_correct_arguments(self.persistent_error_detector, line, service):
                    raise PersistentServiceStartError(line)
                elif self.transient_error_detector is not None \
                        and self._call_detector_with_correct_arguments(self.transient_error_detector, line, service):
                    raise TransientServiceStartError(line)
                elif self._call_detector_with_correct_arguments(self.start_detector, line, service):
                    return True

            assert len(docker_client.containers.list(filters=dict(name=service.name))) == 0
            logs = service.container.logs()
            raise TransientServiceStartError(
                f"No error detected in logs but the container has stopped. Log dump: {logs}")
