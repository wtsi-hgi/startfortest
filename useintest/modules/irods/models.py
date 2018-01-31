from typing import List

import semantic_version

from hgicommon.collections import Metadata as _Metadata
from hgicommon.models import Model
from useintest.services.models import DockerisedService

# Import from semantic version library
Version = semantic_version.Version

# Import from hgicommon library
Metadata = _Metadata


class IrodsResource(Model):
    """
    Model of a iRODS server resource.
    """
    def __init__(self, name: str, host: str, location: str):
        self.name = name
        self.host = host
        self.location = location


# TODO: Extend User in /common
class IrodsUser(Model):
    """
    Model of an iRODS user.
    """
    def __init__(self, username: str, zone: str, password: str=None, admin=False):
        super().__init__()
        self.username = username
        self.password = password
        self.zone = zone
        self.admin = admin


# TODO: Extend ServiceWithUsers in /common
class IrodsDockerisedService(DockerisedService):
    """
    Model of a iRODS service running in Docker.
    """
    def __init__(self):
        super().__init__()
        self.users = []     # type: List[IrodsUser]
        self.version = None
