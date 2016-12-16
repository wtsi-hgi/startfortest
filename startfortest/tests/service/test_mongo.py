import unittest
from abc import ABCMeta

from pymongo import MongoClient

from startfortest.services.mongo import Mongo3DockerisedServiceController, MongoDockerisedServiceController
from startfortest.tests.service._common import TestDockerisedServiceControllerSubclass, create_tests, ControllerType


class _TestMongoDockerisedServiceController(TestDockerisedServiceControllerSubclass[ControllerType], metaclass=ABCMeta):
    """
    Tests for dockerised Mongo service controller.
    """
    def test_start(self):
        service = self._start_service()
        client = MongoClient(service.host, service.port)
        database = client["test-database"]
        posted = {"this": "value"}
        post_id = database.posts.insert_one(posted).inserted_id
        retrieved = database.posts.find_one({"_id": post_id})
        self.assertEqual(retrieved, posted)


# Setup tests
CLASSES_TO_TEST = {Mongo3DockerisedServiceController, MongoDockerisedServiceController}
globals().update(create_tests(_TestMongoDockerisedServiceController, CLASSES_TO_TEST))


# Fix for unittest
del _TestMongoDockerisedServiceController
del TestDockerisedServiceControllerSubclass


if __name__ == "__main__":
    unittest.main()
