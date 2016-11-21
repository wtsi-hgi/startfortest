import unittest
from abc import ABCMeta

from couchdb import Server

from bringupfortest.flavours.couchdb import CouchDBLatestDockerController, CouchDBDockerController, CouchDB1_6Controller
from bringupfortest.tests.flavours._common import TestDockerControllerSubclass, create_tests


class _TestCouchDBDockerController(TestDockerControllerSubclass,  metaclass=ABCMeta):
    """
    Tests for couchdb controller.
    """
    def test_start(self):
        controller = type(self)._get_controller_type()()
        container = controller.start()
        couch = Server("http://%s:%d" % (container.host, container.port))
        database = couch.create("test-database")
        posted = {"this": "value"}
        identifier, revision = database.save(posted)
        self.assertEqual(posted, database[identifier])


# Setup tests
CLASSES_TO_TEST = {CouchDB1_6Controller, CouchDBLatestDockerController, CouchDBDockerController}
globals().update(create_tests(_TestCouchDBDockerController, CLASSES_TO_TEST))


# Fix for unittest
del _TestCouchDBDockerController
del TestDockerControllerSubclass


if __name__ == "__main__":
    unittest.main()
