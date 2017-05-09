import unittest
from abc import ABCMeta

from pymongo import MongoClient

from hgicommon.testing import create_tests, TypeUsedInTest, get_classes_to_test
from useintest.predefined.mongo import Mongo3DockerisedServiceController, MongoLatestDockerisedServiceController, \
    MongoServiceController, mongo_service_controllers
from useintest.services.models import DockerisedServiceWithUsers
from useintest.tests.services.common import TestDockerisedServiceControllerSubclass


class _TestMongoDockerisedServiceController(
    TestDockerisedServiceControllerSubclass[TypeUsedInTest, DockerisedServiceWithUsers], metaclass=ABCMeta):
    """
    Tests for Mongo service controllers.
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
CLASSES_TO_TEST = {Mongo3DockerisedServiceController, MongoLatestDockerisedServiceController}
globals().update(create_tests(_TestMongoDockerisedServiceController, get_classes_to_test(mongo_service_controllers, MongoServiceController)))


# Fix for stupidity of test runners
del _TestMongoDockerisedServiceController, TestDockerisedServiceControllerSubclass, create_tests, get_classes_to_test


if __name__ == "__main__":
    unittest.main()
