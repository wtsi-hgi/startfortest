# Change Log
## 4.1.0 - 2018-01-18
### Added
- Ability to set environment variables for Consul service.

## 4.0.1 - 2017-12-05
### Changed
- Point at which Consul is declared ready to use.

## 4.0.0 - 2017-11-22
### Added
- Support for starting/stopping service inside a context manager.

### Changed
- Consul service controllers now create specialised `ConsulDockerisedService` services.

### Removed
- Support for `CouchDBLatestDockerisedServiceController`.


## 3.2.0 - 2017-11-20
### Added
- Pre-defined support for Consul.
- Configured for PyPi. 

## 3.1.1 - 2017-09-26
### Changed
- Removes containers once stopped.
- No longer gives a warning if the library over-cautiously attempts to stop a stopped container.

## 3.1.0 - 2017-09-20
### Added
- SSH key helper for GitLab.
- Ability to define detectors that get the model of the service as the second parameter, which they could use to 
interact with the service directly.
- Ability to easily override the default, logging based startup monitor via a new `startup_monitor` parameter.
- Pre-defined support for [Bissell](https://github.com/wtsi-hgi/bissell).


## 3.0.0 - 2017-09-19
### Added
- Pre-defined support for GitLab.
- Pre-defined support for Gogs.

### Changed
- Moved a number of models from `useintest.models` to `useintest.services.models`.


## 2.0.0 - 2017-01-11
### Changed
- Switched to using native iRODS controllers, executables and helpers (no longer requires `test-with-irods`).
- Groups predefined controllers by product (e.g. iRODS) not by type (e.g. service).
- Allows quicker testing with latest versions of controllers only.
- Re-branded from `startfortest` to `useintest`.
- Moved documentation to ReadTheDocs.


## 1.0.0 - 2016-11-23
### Added
- First stable release.
