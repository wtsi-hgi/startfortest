import semantic_version
from typing import Set, Optional

from hgicommon.models import Model
from useintest.services.models import DockerisedService


# Import from semantic version library
Version = semantic_version.Version


class User(Model):
    """
    TODO
    """
    def __init__(self, username: str, password: str=None):
        self.username = username
        self.password = password


class ServiceWithUsers(Model):
    """
    TODO
    """
    def __init__(self):
        self.users: Set[User] = {}
        self._root_user: Optional[User] = None

    @property
    def root_user(self) -> Optional[User]:
        """
        TODO
        :return:
        """
        assert self._root_user in self.users
        return self._root_user

    @root_user.setter
    def root_user(self, user: Optional[User]):
        """
        TODO
        :param user:
        :return:
        """
        if user is not None and not user in self.users:
            self.users.add(user)
        self._root_user = user



class DockerisedServiceWithUsers(ServiceWithUsers, DockerisedService):
    """
    TODO
    """
