import unittest
from abc import ABCMeta, abstractmethod

from pymongo import MongoClient

from bringupfortest.controllers import DockerController
from bringupfortest.flavours.mongo import Mongo3DockerController, MongoLatestDockerController, MongoDockerController
from hgicommon.docker.client import create_client


class _TestMongoDockerController(unittest.TestCase, metaclass=ABCMeta):
    """
    Tests for Mongo Docker images
    """
    @staticmethod
    @abstractmethod
    def _get_controller_type(self) -> type:
        """
        TODO
        :param self:
        :return:
        """

    def setUp(self):
        self._docker_client = create_client()

    def test_start(self):
        controller = type(self)._get_controller_type()()
        container = controller.start()
        client = MongoClient(container.host, container.port)
        database = client["test-database"]
        posted = {"this": "value"}
        post_id = database.posts.insert_one(posted).inserted_id
        retrieved = database.posts.find_one({"_id": post_id})
        self.assertEqual(retrieved, posted)

    def test_stop(self):
        controller = type(self)._get_controller_type()()
        container = controller.start()
        assert self._docker_client.inspect_container(container.native_object)["State"]["Status"] == "running"
        controller.stop(container)
        self.assertEqual("exited", self._docker_client.inspect_container(container.native_object)["State"]["Status"])


class TestMongoDockerController(unittest.TestCase):
    """
    Tests for `MongoDockerController`.
    """
    def test_binding(self):
        self.assertIsInstance(MongoDockerController(), DockerController)



for test_type in {Mongo3DockerController, MongoLatestDockerController}:
    globals()[test_type.__name__] = type(
        "Test%s" % test_type.__name__,
        (_TestMongoDockerController,),
        {"_get_controller_type": lambda: test_type}
    )


# Fix for unittest
del _TestMongoDockerController


if __name__ == "__main__":
    unittest.main()
