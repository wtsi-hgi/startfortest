import unittest
from abc import ABCMeta

from pymongo import MongoClient

from startfortest.service.mongo import Mongo3DockerController, MongoLatestDockerController, MongoDockerController
from startfortest.tests.service._common import TestDockerControllerSubclass, create_tests


class _TestMongoDockerController(TestDockerControllerSubclass, metaclass=ABCMeta):
    """
    Tests for Mongo Docker images
    """
    def test_start(self):
        controller = type(self)._get_controller_type()()
        container = controller.start()
        client = MongoClient(container.host, container.port)
        database = client["test-database"]
        posted = {"this": "value"}
        post_id = database.posts.insert_one(posted).inserted_id
        retrieved = database.posts.find_one({"_id": post_id})
        self.assertEqual(retrieved, posted)


# Setup tests
CLASSES_TO_TEST = {Mongo3DockerController, MongoLatestDockerController, MongoDockerController}
globals().update(create_tests(_TestMongoDockerController, CLASSES_TO_TEST))


# Fix for unittest
del _TestMongoDockerController
del TestDockerControllerSubclass


if __name__ == "__main__":
    unittest.main()
