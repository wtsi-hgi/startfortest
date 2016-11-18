import atexit
import logging
import math
from abc import ABCMeta, abstractmethod
from threading import Thread, Event
from typing import Dict, Iterator, Optional, List, Callable

from docker.errors import APIError

from bringupfortest.exceptions import ContainerStartException
from bringupfortest.models import Container
from hgicommon.docker.client import create_client
from hgicommon.helpers import create_random_string, get_open_port

_logger = logging.getLogger(__name__)


class Controller(metaclass=ABCMeta):
    """
    TODO
    """
    @abstractmethod
    def _start(self) -> Container:
        """
        TODO
        """

    @abstractmethod
    def _stop(self, container: Container):
        """
        TODO
        """

    @abstractmethod
    def _wait_until_started(self, container: Container, started: Event):
        """
        TODO
        :param container:
        :param started:
        :return:
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
        container = None
        tries = 0
        started = Event()
        while not started.is_set():
            if tries > self.start_retries:
                raise ContainerStartException()
            container = self._start()
            # FIXME: Thread needs to stop safely!
            Thread(target=self._wait_until_started, args=(container, started)).start()
            started.wait(timeout=self.start_timeout if self.start_timeout < math.inf else None)
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
                 start_timeout: int=math.inf, start_retries: int=math.inf):
        super().__init__(start_timeout, start_retries)
        self.repository = repository
        self.tag = tag
        self.ports = ports
        self.start_detector = start_detector
        self._log_iterator = dict()     # type: Dict[Container, Iterator]

    def _start(self):
        _docker_client = DockerController._docker_client

        if self._get_docker_image(self.repository, self.tag) is None:
            # Docker image doesn't exist locally: getting from DockerHub
            _docker_client.pull(self.repository, self.tag)

        container = Container()
        container.name = create_random_string(prefix="%s-" % self.repository)
        container.ports = {port: get_open_port() for port in self.ports}
        container.native_object = _docker_client.create_container(
            image=self._get_docker_image(self.repository, self.tag),
            name=container.name,
            ports=list(container.ports.values()),
            host_config=_docker_client.create_host_config(port_bindings=container.ports))

        if self.stop_on_exit:
            atexit.register(self.stop, container)
        _docker_client.start(container.native_object)

        return container

    def _stop(self, container: Container):
        if container in self._log_iterator:
            del self._log_iterator[container]
        try:
            DockerController._docker_client.kill(container.native_object)
        except Exception as e:
            ignore = False
            if isinstance(e, APIError):
                ignore = "is not running" in str(e.explanation)
            if not ignore:
                raise e

    def _wait_until_started(self, container: Container, started: Event):
        for line in DockerController._docker_client.logs(container.native_object, stream=True):
            line = str(line)
            logging.debug(line)
            if self.start_detector(line):
                started.set()
                break
