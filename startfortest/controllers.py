import atexit
import logging
import math
from abc import ABCMeta, abstractmethod
from typing import Dict, Iterator, Optional, List, Callable, TypeVar, Generic, Type

from docker.errors import APIError
from stopit import ThreadingTimeout, TimeoutException

from hgicommon.docker.client import create_client
from hgicommon.helpers import create_random_string, get_open_port
from startfortest._docker_helpers import is_docker_container_running
from startfortest.exceptions import ServiceStartException, TransientServiceStartException, \
    PersistentServiceStartException
from startfortest.models import Service, DockerisedService

_logger = logging.getLogger(__name__)

ServiceModel = TypeVar("ServiceModel", bound=Service)
DockerisedServiceModel = TypeVar("DockerisedServiceModel", bound=DockerisedService)


class ServiceController(Generic[ServiceModel], metaclass=ABCMeta):
    """
    Service controller.
    """
    def __init__(self, service_model: Type[ServiceModel]):
        """
        Constructor.
        :param service_model: the type of model for the services this controller handles
        """
        # TODO: It would nice to do `ServiceModel()` but I don't think this is possible in Python
        self._service_model = service_model

    @abstractmethod
    def start_service(self) -> ServiceModel:
        """
        Starts a service.
        :raises ServiceStartException: service could not be started (see logs for more information)
        :return: model of the started service
        """

    @abstractmethod
    def stop_service(self, service: ServiceModel):
        """
        Stops the given service.
        :param service: model of the service to stop
        """


class ContainerisedServiceController(ServiceController[ServiceModel], metaclass=ABCMeta):
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

    def __init__(self, service_model: Type[ServiceModel], start_timeout: float=math.inf, start_tries: int=math.inf,
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

    def start_service(self) -> ServiceModel:
        service = self._service_model()
        if self.stop_on_exit:
            atexit.register(self.stop_service, service)

        started = False
        tries = 0
        while not started:
            if tries >= self.start_tries:
                raise ServiceStartException()
            self._start(service)
            try:
                if self.start_timeout is not math.inf:
                    with ThreadingTimeout(self.start_timeout, swallow_exc=False):
                        started = self._wait_until_started(service)
                else:
                    started = self._wait_until_started(service)
            except TimeoutException as e:
                _logger.warning(e)
            except TransientServiceStartException as e:
                _logger.warning(e)

            tries += 1
        assert service is not None
        return service

    def stop_service(self, service: ServiceModel):
        self._stop(service)


class DockerisedServiceController(ContainerisedServiceController[ServiceModel], metaclass=ABCMeta):
    """
    Controller of Docker containers running a service brought up for testing.
    """
    @staticmethod
    def _get_docker_image(repository: str, tag: str) -> Optional[str]:
        """
        Gets the identifier of the docker image from the given repository with the given tag.
        :param repository: the Dockerhub repository
        :param tag: the image tag
        :return: image identifier or `None` if it has not been pulled
        """
        identifiers = create_client().images("%s:%s" % (repository, tag), quiet=True)
        return identifiers[0] if len(identifiers) > 0 else None

    def __init__(self, service_model: Type[ServiceModel], repository: str, tag: str, ports: List[int],
                 start_detector: Callable[[str], bool],
                 persistent_error_detector: Callable[[str], bool]=None,
                 transient_error_detector: Callable[[str], bool]=None,
                 start_timeout: int=math.inf, start_tries: int=math.inf):
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
        """
        super().__init__(service_model, start_timeout, start_tries)
        self.repository = repository
        self.tag = tag
        self.ports = ports
        self.start_detector = start_detector
        self.persistent_error_detector = persistent_error_detector
        self.transient_error_detector = transient_error_detector
        self._log_iterator = dict()     # type: Dict[Service, Iterator]

    def _start(self, service: DockerisedService):
        _docker_client = create_client()

        if self._get_docker_image(self.repository, self.tag) is None:
            # Docker image doesn't exist locally: getting from DockerHub
            _docker_client.pull(self.repository, self.tag)

        service.name = create_random_string(prefix="%s-" % self.repository)
        service.ports = {port: get_open_port() for port in self.ports}
        service.container = _docker_client.create_container(
            image=self._get_docker_image(self.repository, self.tag),
            name=service.name,
            ports=list(service.ports.values()),
            host_config=_docker_client.create_host_config(port_bindings=service.ports))

        _docker_client.start(service.container)

    def _stop(self, service: DockerisedService):
        if service in self._log_iterator:
            del self._log_iterator[service]
        if service.container:
            try:
                create_client().kill(service.container)
            except Exception as e:
                ignore = False
                if isinstance(e, APIError):
                    ignore = "is not running" in str(e.explanation)
                if not ignore:
                    raise e

    def _wait_until_started(self, service: DockerisedService) -> bool:
        for line in create_client().logs(service.container, stream=True):
            line = str(line)
            logging.debug(line)
            if self.start_detector(line):
                return True
            elif self.persistent_error_detector is not None and self.persistent_error_detector(line):
                raise PersistentServiceStartException(line)
            elif self.transient_error_detector is not None and self.transient_error_detector(line):
                raise TransientServiceStartException(line)

        assert not is_docker_container_running(service)
        raise TransientServiceStartException("No error detected in logs but the container has stopped")
