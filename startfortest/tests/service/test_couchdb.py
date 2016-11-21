import unittest
from abc import ABCMeta

from couchdb import Server

from startfortest.service.couchdb import CouchDBDockerController, CouchDB1_6DockerController
from startfortest.tests.service._common import TestDockerControllerSubclass, create_tests


class _TestCouchDBDockerController(TestDockerControllerSubclass,  metaclass=ABCMeta):
    """
    Tests for couchdb controller.
    """
    def test_start(self):
        controller = type(self)._get_controller_type()()
        container = controller.start_service()
        couch = Server("http://%s:%d" % (container.host, container.port))
        database = couch.create("test-database")
        posted = {"this": "value"}
        identifier, revision = database.save(posted)
        self.assertEqual(posted, database[identifier])


# Setup tests
CLASSES_TO_TEST = {CouchDB1_6DockerController, CouchDBDockerController}
globals().update(create_tests(_TestCouchDBDockerController, CLASSES_TO_TEST))


# Fix for unittest
del _TestCouchDBDockerController
del TestDockerControllerSubclass


if __name__ == "__main__":
    unittest.main()
