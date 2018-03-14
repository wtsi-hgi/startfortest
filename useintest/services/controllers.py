import atexit
import math
import socket
from abc import ABCMeta, abstractmethod
from inspect import signature
from typing import Dict, Iterator, List, Callable, TypeVar, Generic, Type, Union, Any
from uuid import uuid4

import requests
from docker.errors import NotFound
from requests import Response
from time import sleep
from timeout_decorator import timeout_decorator

from useintest._logging import create_logger
from useintest.common import docker_client
from useintest.executables.common import pull_docker_image
from useintest.services.exceptions import ServiceStartError, TransientServiceStartError, PersistentServiceStartError
from useintest.services.models import Service, DockerisedService, DockerisedServiceWithUsers

ServiceType = TypeVar("ServiceType", bound=Service)
DockerisedServiceType = TypeVar("DockerisedServiceType", bound=DockerisedService)
DockerisedServiceWithUsersType = TypeVar("DockerisedServiceWithUsersType", bound=DockerisedServiceWithUsers)
LogListener = Union[Callable[[str, DockerisedService], bool], Callable[[str], bool]]

logger = create_logger(__name__)

_DOCKER_LOG_ENCODING = "utf-8"


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
    def start_service(self, runtime_configuration: Dict=None) -> ServiceType:
        """
        Starts a service.
        :param runtime_configuration: additional runtime configuration
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
    def _start(self, service: Service, runtime_configuration: Dict):
        """
        Starts a container.
        :param service: model of the service to start
        :param runtime_configuration: additional runtime configuration
        """

    @abstractmethod
    def _stop(self, service: Service):
        """
        Stops the given container.
        :param service: model of the service to stop
        """

    def __init__(self, service_model: Type[ServiceType], start_timeout: float=math.inf, start_tries: int=10,
                 stop_on_exit: bool=True, startup_monitor: Callable[[ServiceType], bool]=None):
        """
        Constructor.
        :param stop_on_exit: see `Container.__init__`
        :param start_timeout: timeout before for container start
        :param start_tries: number of times to try to start the container before giving up (will only try once if a
        `PersistentServiceStartException` is raised
        :param stop_on_exit: whether to stop all started containers on exit
        :param startup_monitor: callable that should block until the service, given as the first parameter is known to
        have started and is ready for use. Should raise a `ServiceStartException` if service is not going to start
        """
        super().__init__(service_model)
        self.start_timeout = start_timeout
        self.start_tries = start_tries
        self.stop_on_exit = stop_on_exit
        self.startup_monitor = startup_monitor

    def start_service(self, runtime_configuration: Dict=None) -> ServiceType:
        service = self._service_model()
        assert service is not None
        if self.stop_on_exit:
            atexit.register(self.stop_service, service)

        tries = 0
        while tries < self.start_tries:
            if tries > 0:
                self._stop(service)
            self._start(service, runtime_configuration if runtime_configuration is not None else {})
            try:
                if self.start_timeout is not math.inf:
                    @timeout_decorator.timeout(self.start_timeout, timeout_exception=TimeoutError)
                    def _wrapped_wait_until_started(service: ServiceType) -> bool:
                        return self._wait_until_started(service)
                    _wrapped_wait_until_started(service)
                else:
                    self._wait_until_started(service)
                return service
            except TimeoutError as e:
                logger.warning(e)
            except TransientServiceStartError as e:
                logger.warning(e)
            tries += 1

        raise ServiceStartError()

    def stop_service(self, service: ServiceType):
        self._stop(service)

    def _wait_until_started(self, service: ServiceType):
        """
        Blocks until the given container has started.
        :raises ServiceStartException: raised if service cannot be started
        :param service: the service
        """
        if self.startup_monitor is None:
            raise ValueError("No startup monitor set")
        return self.startup_monitor(service)


class DockerisedServiceController(
        Generic[DockerisedServiceType], ContainerisedServiceController[DockerisedServiceType], metaclass=ABCMeta):
    """
    Controller of Docker containers running a service brought up for testing.
    """
    @staticmethod
    def _call_detector_with_correct_arguments(detector: Callable, line: str, service: DockerisedServiceType) -> bool:
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

    def __init__(self, service_model: Type[ServiceType], repository: str, tag: str, ports: List[int], *,
                 start_timeout: int=math.inf, start_tries: int=math.inf, additional_run_settings: Dict[str, Any]=None,
                 pull: bool=True,
                 start_log_detector: LogListener=None,
                 persistent_error_log_detector: LogListener=None,
                 transient_error_log_detector: LogListener=None,
                 startup_monitor: Callable[[ServiceType], bool]=None,
                 start_http_detector: Callable[[Response], bool]=None,
                 start_http_detection_endpoint: str=""):
        """
        Constructor.
        :param service_model: see `ServiceController.__init__`
        :param repository: the repository of the service to start
        :param tag: the repository tag of the service to start
        :param ports: the ports the service exposes
        :param start_timeout: timeout for starting containers
        :param start_tries: number of times to try starting the containerised service
        :param additional_run_settings: other run settings (see https://docker-py.readthedocs.io/en/1.2.3/api/#create_container)
        :param pull: whether to always pull from source repository
        :param start_log_detector: callable that detects if the service is ready for use from the logs
        :param persistent_error_log_detector: callable that detects if the service is unable to start
        :param transient_error_log_detector: callable that detects if the service encountered a transient error
        :param start_http_detector: callable that detects if the service is ready for use based on given HTTP response
        :param start_http_detection_endpoint: endpoint to call that should respond if the service has started
        """
        if startup_monitor and (start_log_detector or persistent_error_log_detector or transient_error_log_detector or
                                start_http_detector):
            raise ValueError("Cannot set `startup_monitor` in conjunction with any other detector")

        super().__init__(service_model, start_timeout, start_tries, startup_monitor=startup_monitor)
        self.repository = repository
        self.tag = tag
        self.ports = ports
        self.run_settings = additional_run_settings if additional_run_settings is not None else {}
        self.pull = pull
        self.start_log_detector = start_log_detector
        self.persistent_error_log_detector = persistent_error_log_detector
        self.transient_error_log_detector = transient_error_log_detector
        self.start_http_detector = start_http_detector
        self.start_http_detection_endpoint = start_http_detection_endpoint

        self._log_iterator: Dict[Service, Iterator] = dict()

    def _start(self, service: DockerisedServiceType, runtime_configuration: Dict):
        if self.pull:
            image = docker_client.images.pull(self.repository, tag=self.tag)
        else:
            image = docker_client.images.get(f"{self.repository}:{self.tag}")

        service.name = f"{self.repository.split('/')[-1]}-{uuid4()}"
        service.ports = {port: _get_open_port() for port in self.ports}
        service.controller = self

        create_kwargs = dict(self.run_settings)
        create_kwargs.update(runtime_configuration)
        container = docker_client.containers.create(
            image=image.id,
            name=service.name,
            ports=service.ports,
            detach=True,
            **create_kwargs)
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

    def _wait_until_started(self, service: DockerisedServiceType):
        if self.startup_monitor is not None:
            return self.startup_monitor(service)
        else:
            if self.start_log_detector:
                self._wait_until_log_indicates_start(service)
            if self.start_http_detector:
                self._wait_until_http_indicates_start(service)

    def _wait_until_log_indicates_start(self, service: DockerisedServiceType):
        """
        Blocks until container log indicates that the service has started.
        :param service: starting service
        :raises ServiceStartException: raised if service cannot be started
        """
        log_stream = service.container.logs(stream=True)
        for line in log_stream:
            # XXX: Although non-streamed logs are returned as a string, the generator returns bytes!?
            # http://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.Container.logs
            line = line.decode(_DOCKER_LOG_ENCODING)
            logger.debug(line)

            if self.persistent_error_log_detector is not None \
                    and self._call_detector_with_correct_arguments(self.persistent_error_log_detector, line, service):
                raise PersistentServiceStartError(line)
            elif self.transient_error_log_detector is not None \
                    and self._call_detector_with_correct_arguments(self.transient_error_log_detector, line, service):
                raise TransientServiceStartError(line)
            elif self._call_detector_with_correct_arguments(self.start_log_detector, line, service):
                return

        logs = service.container.logs()
        raise TransientServiceStartError(f"No error detected in logs but the container has stopped. Log dump: "
                                         f"{logs.decode(_DOCKER_LOG_ENCODING)}")

    def _wait_until_http_indicates_start(self, service: DockerisedServiceType):
        """
        Blocks until http endpoint indicates that the service has started.
        :param service: starting service
        """
        started = False
        while not started:
            try:
                response = requests.head(f"http://{service.host}:{service.port}/{self.start_http_detection_endpoint}")
                started = self.start_http_detector(response)
            except requests.exceptions.ConnectionError:
                pass
            if not started:
                sleep(0.1)
