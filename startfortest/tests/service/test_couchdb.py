import unittest
from abc import ABCMeta

from couchdb import Server

from startfortest.services.couchdb import CouchDBDockerisedServiceController, CouchDB1_6DockerisedServiceController
from startfortest.tests.service._common import TestDockerisedServiceControllerSubclass, create_tests, ControllerType


class _TestCouchDBDockerisedServiceController(
    TestDockerisedServiceControllerSubclass[ControllerType], metaclass=ABCMeta):
    """
    Tests for Dockerised CouchDB service controller.
    """
    def test_start(self):
        service = self._start_service()
        couch = Server("http://%s:%d" % (service.host, service.port))
        database = couch.create("test-database")
        posted = {"this": "value"}
        identifier, revision = database.save(posted)
        self.assertEqual(posted, database[identifier])


# Setup tests
CLASSES_TO_TEST = {CouchDB1_6DockerisedServiceController, CouchDBDockerisedServiceController}
globals().update(create_tests(_TestCouchDBDockerisedServiceController, CLASSES_TO_TEST))


# Fix for unittest
del _TestCouchDBDockerisedServiceController
del TestDockerisedServiceControllerSubclass


if __name__ == "__main__":
    unittest.main()
