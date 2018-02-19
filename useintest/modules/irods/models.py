from typing import Any

import semantic_version

from useintest.common import UseInTestModel
from useintest.services.models import DockerisedServiceWithUsers, User

# Import from semantic version library
Version = semantic_version.Version


class IrodsResource(UseInTestModel):
    """
    An iRODS server resource.
    """
    def __init__(self, name: str, host: str, location: str):
        self.name = name
        self.host = host
        self.location = location


class IrodsUser(User):
    """
    An iRODS user.
    """
    def __init__(self, username: str, zone: str, password: str=None, admin: bool=False):
        super().__init__(username, password)
        self.zone = zone
        self.admin = admin

    def __eq__(self, other: Any) -> bool:
        return super().__eq__(other) \
               and other.zone == self.zone \
               and other.admin == self.admin

    def __hash__(self) -> hash:
        return hash(str(super().__hash__()) + self.zone + str(self.admin))


class IrodsDockerisedService(DockerisedServiceWithUsers[IrodsUser]):
    """
    An iRODS service running in Docker.
    """
    def __init__(self):
        super().__init__()
        self.version: Version = None
