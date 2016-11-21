import atexit
import logging
import math
from abc import ABCMeta, abstractmethod
from typing import Dict, Iterator, Optional, List, Callable

import time
from docker.errors import APIError
from stopit import ThreadingTimeout
from stopit import TimeoutException

from bringupfortest._helpers import is_docker_container_running
from bringupfortest.exceptions import ContainerStartException, TransientContainerStartException, \
    PersistentContainerStartException
from bringupfortest.models import Container
from hgicommon.docker.client import create_client
from hgicommon.helpers import create_random_string, get_open_port

_logger = logging.getLogger(__name__)


class Controller(metaclass=ABCMeta):
    """
    TODO
    """
    @abstractmethod
    def _start(self, container: Container):
        """
        Starts a container.
        """

    @abstractmethod
    def _stop(self, container: Container):
        """
        TODO
        """

    @abstractmethod
    def _wait_until_started(self, container: Container) -> bool:
        """
        TODO
        :param container:
        :param started:
        :return: `True` if the container has started successfully
        """

    def __init__(self, start_timeout: float=math.inf, start_retries: int=math.inf, stop_on_exit: bool=True):
        self.start_timeout = start_timeout
        self.start_retries = start_retries
        self.stop_on_exit = stop_on_exit

    def start(self) -> Container:
        """
        TODO
        :return:
        """
        container = Container()
        if self.stop_on_exit:
            atexit.register(self.stop, container)

        started = False
        tries = 0
        while not started:
            if tries >= self.start_retries:
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

    def stop(self, container: Container):
        """
        TODO
        :return:
        """
        self._stop(container)


class DockerController(Controller, metaclass=ABCMeta):
    """
    TODO
    """
    _docker_client = create_client()

    @staticmethod
    def _get_docker_image(repository: str, tag: str) -> Optional[str]:
        """
        TODO
        :return: image identifier or `None` if it hasn't been pulled
        """
        identifiers = DockerController._docker_client.images("%s:%s" % (repository, tag), quiet=True)
        return identifiers[0] if len(identifiers) > 0 else None

    def __init__(self, repository: str, tag: str, ports: List[int], start_detector: Callable[[str], bool],
                 persistent_error_detector: Callable[[str], bool]=None,
                 transient_error_detector: Callable[[str], bool]=None,
                 start_timeout: int=math.inf, start_retries: int=math.inf):
        super().__init__(start_timeout, start_retries)
        self.repository = repository
        self.tag = tag
        self.ports = ports
        self.start_detector = start_detector
        self.persistent_error_detector = persistent_error_detector
        self.transient_error_detector = transient_error_detector
        self._log_iterator = dict()     # type: Dict[Container, Iterator]

    def _start(self, container: Container):
        _docker_client = DockerController._docker_client

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
                DockerController._docker_client.kill(container.native_object)
            except Exception as e:
                ignore = False
                if isinstance(e, APIError):
                    ignore = "is not running" in str(e.explanation)
                if not ignore:
                    raise e

    def _wait_until_started(self, container: Container) -> bool:
        for line in DockerController._docker_client.logs(container.native_object, stream=True):
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
