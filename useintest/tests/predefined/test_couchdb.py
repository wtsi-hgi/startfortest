import unittest
from abc import ABCMeta

from couchdb import Server

from hgicommon.testing import TypeToTest, create_tests, get_classes_to_test
from useintest.predefined.couchdb import couchdb_service_controllers, CouchDBServiceController
from useintest.tests.service.common import TestDockerisedServiceControllerSubclass


class _TestCouchDBDockerisedServiceController(TestDockerisedServiceControllerSubclass[TypeToTest], metaclass=ABCMeta):
    """
    Tests for CouchDB service controllers.
    """
    def test_start(self):
        service = self._start_service()
        couch = Server("http://%s:%d" % (service.host, service.port))
        database = couch.create("test-database")
        posted = {"this": "value"}
        identifier, revision = database.save(posted)
        self.assertEqual(posted, database[identifier])


# Setup tests
globals().update(create_tests(_TestCouchDBDockerisedServiceController, get_classes_to_test(couchdb_service_controllers, CouchDBServiceController)))


# Fix for stupidity of test runners
del _TestCouchDBDockerisedServiceController, TestDockerisedServiceControllerSubclass, create_tests, get_classes_to_test


if __name__ == "__main__":
    unittest.main()
