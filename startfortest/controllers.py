import atexit
import logging
import math
from abc import ABCMeta, abstractmethod
from typing import Dict, Iterator, Optional, List, Callable, TypeVar, Generic, Type

from docker.errors import APIError
from stopit import ThreadingTimeout, TimeoutException

from hgicommon.docker.client import create_client
from hgicommon.docker.models import Container
from hgicommon.helpers import create_random_string, get_open_port
from startfortest._docker_helpers import is_docker_container_running
from startfortest.exceptions import ContainerStartException, TransientContainerStartException, \
    PersistentContainerStartException
from startfortest.models import Service, DockerisedService

_logger = logging.getLogger(__name__)

ServiceModel = TypeVar("ServiceModel", bound=Service)
DockerisedServiceModel = TypeVar("DockerisedServiceModel", bound=DockerisedService)


class ServerController(Generic[ServiceModel], metaclass=ABCMeta):
    """
    Server controller.
    """
    def __init__(self, service_model: Type[ServiceModel]):
        """
        TODO
        :param service_model:
        """
        # TODO: It would nice to do `ServiceModel()` but I don't think this is possible in Python
        self._service_model = service_model

    @abstractmethod
    def start_service(self) -> ServiceModel:
        """
        Starts a container.
        :raises ContainerStartException: container could not be started (see logs for more information)
        :return: the started container
        """

    @abstractmethod
    def stop_service(self, service: ServiceModel):
        """
        Stops the given container.
        :param service: the container to stop
        """


class ContainerServerController(ServerController[ServiceModel], metaclass=ABCMeta):
    """
    ServerController of containers running a service brought up for testing.
    """
    @abstractmethod
    def _start(self, container: Container):
        """
        Starts a container.
        :param container: the container to start
        """

    @abstractmethod
    def _stop(self, container: Container):
        """
        Stops the given container.
        :param container: the container to stop
        """

    @abstractmethod
    def _wait_until_started(self, container: Service) -> bool:
        """
        Blocks until the given container has started.
        :raises ContainerStartException: raised if container cannot be started
        :param container: the container
        :return: `True` if the container has started successfully
        """

    def __init__(self, service_model: Type[ServiceModel], start_timeout: float=math.inf, start_tries: int=math.inf,
                 stop_on_exit: bool=True):
        """
        Constructor.
        :param stop_on_exit: see `Container.__init__`
        :param start_timeout: timeout before for container start
        :param start_tries: number of times to try to start the container before giving up (will only try once if a
        `PersistentContainerStartException` is raised
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
                raise ContainerStartException()
            self._start(service)
            try:
                if self.start_timeout is not math.inf:
                    with ThreadingTimeout(self.start_timeout, swallow_exc=False):
                        started = self._wait_until_started(service)
                else:
                    started = self._wait_until_started(service)
            except TimeoutException as e:
                _logger.warning(e)
            except TransientContainerStartException as e:
                _logger.warning(e)

            tries += 1
        assert service is not None
        return service

    def stop_service(self, service: ServiceModel):
        self._stop(service)


class DockerisedServiceController(ContainerServerController[ServiceModel], metaclass=ABCMeta):
    """
    ServerController of Docker containers running a service brought up for testing.
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
        :param service_model: see `ServerController.__init__`
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

    def _start(self, container: DockerisedService):
        _docker_client = create_client()

        if self._get_docker_image(self.repository, self.tag) is None:
            # Docker image doesn't exist locally: getting from DockerHub
            _docker_client.pull(self.repository, self.tag)

        container.name = create_random_string(prefix="%s-" % self.repository)
        container.ports = {port: get_open_port() for port in self.ports}
        container.container = _docker_client.create_container(
            image=self._get_docker_image(self.repository, self.tag),
            name=container.name,
            ports=list(container.ports.values()),
            host_config=_docker_client.create_host_config(port_bindings=container.ports))

        _docker_client.start(container.container)

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
                raise PersistentContainerStartException(line)
            elif self.transient_error_detector is not None and self.transient_error_detector(line):
                raise TransientContainerStartException(line)

        assert not is_docker_container_running(service)
        raise TransientContainerStartException("No error detected in logs but the container has stopped")
