import atexit
import logging
import math
from abc import ABCMeta, abstractmethod
from typing import Dict, Iterator, Optional, List, Callable

from docker.errors import APIError
from stopit import ThreadingTimeout, TimeoutException

from startfortest._docker_helpers import is_docker_container_running
from startfortest.exceptions import ContainerStartException, TransientContainerStartException, \
    PersistentContainerStartException
from startfortest.models import Container
from hgicommon.docker.client import create_client
from hgicommon.helpers import create_random_string, get_open_port

_logger = logging.getLogger(__name__)


class Controller(metaclass=ABCMeta):
    """
    Controller of containers running service brought up for testing.
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
    def _wait_until_started(self, container: Container) -> bool:
        """
        Blocks until the given container has started.
        :raises ContainerStartException: raised if container canot be started
        :param container: the container
        :return: `True` if the container has started successfully
        """

    def __init__(self, start_timeout: float=math.inf, start_tries: int=math.inf, stop_on_exit: bool=True):
        """
        Constructor.
        :param start_timeout: timeout before for container start
        :param start_tries: number of times to try to start the container before giving up (will only try once if a
        `PersistentContainerStartException` is raised
        :param stop_on_exit: whether to stop all started containers on exit
        """
        self.start_timeout = start_timeout
        self.start_tries = start_tries
        self.stop_on_exit = stop_on_exit

    def start_service(self) -> Container:
        """
        Starts a container.
        :raises ContainerStartException: container could not be started (see logs for more information)
        :return: the started container
        """
        container = Container()
        if self.stop_on_exit:
            atexit.register(self.stop_service, container)

        started = False
        tries = 0
        while not started:
            if tries >= self.start_tries:
                raise ContainerStartException()
            self._start(container)
            try:
                if self.start_timeout is not math.inf:
                    with ThreadingTimeout(self.start_timeout, swallow_exc=False):
                        started = self._wait_until_started(container)
                else:
                    started = self._wait_until_started(container)
            except TimeoutException as e:
                _logger.warning(e)
            except TransientContainerStartException as e:
                _logger.warning(e)

            tries += 1
        assert container is not None
        return container

    def stop_service(self, container: Container):
        """
        Stops the given container.
        :param container: the container to stop
        """
        self._stop(container)


class DockerController(Controller, metaclass=ABCMeta):
    """
    Controller of Docker containers running service brought up for testing.
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

    def __init__(self, repository: str, tag: str, ports: List[int], start_detector: Callable[[str], bool],
                 persistent_error_detector: Callable[[str], bool]=None,
                 transient_error_detector: Callable[[str], bool]=None,
                 start_timeout: int=math.inf, start_tries: int=math.inf):
        """
        Constructor.
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
        super().__init__(start_timeout, start_tries)
        self.repository = repository
        self.tag = tag
        self.ports = ports
        self.start_detector = start_detector
        self.persistent_error_detector = persistent_error_detector
        self.transient_error_detector = transient_error_detector
        self._log_iterator = dict()     # type: Dict[Container, Iterator]

    def _start(self, container: Container):
        _docker_client = create_client()

        if self._get_docker_image(self.repository, self.tag) is None:
            # Docker image doesn't exist locally: getting from DockerHub
            _docker_client.pull(self.repository, self.tag)

        container.name = create_random_string(prefix="%s-" % self.repository)
        container.ports = {port: get_open_port() for port in self.ports}
        container.native_object = _docker_client.create_container(
            image=self._get_docker_image(self.repository, self.tag),
            name=container.name,
            ports=list(container.ports.values()),
            host_config=_docker_client.create_host_config(port_bindings=container.ports))

        _docker_client.start(container.native_object)

    def _stop(self, container: Container):
        if container in self._log_iterator:
            del self._log_iterator[container]
        if container.native_object:
            try:
                create_client().kill(container.native_object)
            except Exception as e:
                ignore = False
                if isinstance(e, APIError):
                    ignore = "is not running" in str(e.explanation)
                if not ignore:
                    raise e

    def _wait_until_started(self, container: Container) -> bool:
        for line in create_client().logs(container.native_object, stream=True):
            line = str(line)
            logging.debug(line)
            if self.start_detector(line):
                return True
            elif self.persistent_error_detector is not None and self.persistent_error_detector(line):
                raise PersistentContainerStartException(line)
            elif self.transient_error_detector is not None and self.transient_error_detector(line):
                raise TransientContainerStartException(line)

        assert not is_docker_container_running(container)
        raise TransientContainerStartException("No error detected in logs but container has stopped")
