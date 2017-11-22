from useintest.services._builders import DockerisedServiceControllerTypeBuilder

common_setup = {
    "repository": "couchdb",
    "start_detector": lambda log_line: "Apache CouchDB has started" in log_line,
    "persistent_error_detector": lambda log_line: "no space left on device" in log_line,
    "ports": [5984]
}

CouchDB1_6DockerisedServiceController = DockerisedServiceControllerTypeBuilder(
    name="CouchDB1_6DockerisedServiceController",
    tag="1.6",
    **common_setup).build()   # type: type


CouchDB1_6ServiceController = CouchDB1_6DockerisedServiceController
CouchDBServiceController = CouchDB1_6ServiceController

couchdb_service_controllers = {CouchDB1_6ServiceController, CouchDBServiceController}
