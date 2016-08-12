from typing import List

import semantic_version

import hgicommon
from hgicommon.models import Model

from hgicommon.docker.models import Container

# Import from semantic version library
Version = semantic_version.Version

# Import from hgicommon library
Metadata = hgicommon.collections.Metadata


class IrodsUser(Model):
    """
    Model of an iRODS user.
    """
    def __init__(self, username: str, zone: str, password: str=None, admin=False):
        self.username = username
        self.password = password
        self.zone = zone
        self.admin = admin


class IrodsServer(Model):
    """
    Model of an iRODS server.
    """
    def __init__(self, host: str=None, port: int=None, users: List[IrodsUser]=None, version: Version=None):
        super().__init__()
        self.host = host
        self.port = port
        self.users = [] if users is None else users     # type: List[IrodsUser]
        self.version = version


class ContainerisedIrodsServer(IrodsServer, Container):
    """
    Model of an iRODS server that runs in a container.
    """
    def __init__(self):
        super().__init__()


class IrodsResource(Model):
    """
    Model of a iRODS server resource.
    """
    def __init__(self, name: str, host: str, location: str):
        self.name = name
        self.host = host
        self.location = location
