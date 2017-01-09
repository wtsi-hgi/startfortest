import unittest
from abc import ABCMeta

from pymongo import MongoClient

from hgicommon.testing import create_tests, TypeToTest, get_classes_to_test
from useintest.predefined.mongo import Mongo3DockerisedServiceController, MongoDockerisedServiceController, \
    MongoController, mongo_controllers
from useintest.tests.service.common import TestDockerisedServiceControllerSubclass


class _TestMongoDockerisedServiceController(TestDockerisedServiceControllerSubclass[TypeToTest], metaclass=ABCMeta):
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
globals().update(create_tests(_TestMongoDockerisedServiceController, get_classes_to_test(mongo_controllers, MongoController)))


# Fix for stupidity of test runners
del _TestMongoDockerisedServiceController, TestDockerisedServiceControllerSubclass, create_tests, get_classes_to_test


if __name__ == "__main__":
    unittest.main()