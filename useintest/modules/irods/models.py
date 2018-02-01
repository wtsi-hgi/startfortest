from typing import List

import semantic_version

from useintest.common import UseInTestModel
from useintest.services.models import DockerisedService

# Import from semantic version library
Version = semantic_version.Version


class IrodsResource(UseInTestModel):
    """
    Model of a iRODS server resource.
    """
    def __init__(self, name: str, host: str, location: str):
        self.name = name
        self.host = host
        self.location = location


# TODO: Extend User in /common
class IrodsUser(UseInTestModel):
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
        self.users: List[IrodsUser] = []
        self.version: Version = None
