from abc import ABCMeta

from useintest.models import DockerisedServiceWithUsers, User
from useintest.services._builders import DockerisedServiceControllerTypeBuilder
from useintest.services.controllers import DockerisedServiceController, ServiceModel

_ROOT_USERNAME = "root"
_ROOT_PASSWORD = "gitlab123"

_repository = "gitlab/gitlab-ce"
_ports = [80, 433, 22]
_start_detector = lambda log_line: "==> /var/log/gitlab/redis/current <==" in log_line
_persistent_error_detector = lambda log_line: "o space left on device" in log_line
_environment_variables = {"GITLAB_ROOT_PASSWORD": _ROOT_PASSWORD}


class GitLabBaseServiceController(DockerisedServiceController[ServiceModel], metaclass=ABCMeta):
    """
    BAse class for GitLab service controllers.
    """
    def start_service(self) -> DockerisedServiceWithUsers:
        service = super().start_service()
        # TODO: The generic does not imply a bound on `DockerisedServiceWithUsers`. Therefore a static compiler will not
        # be happy at this point because all it knows is that service is bound on `Service`
        service.root_user = User(_ROOT_USERNAME, _ROOT_PASSWORD)
        return service


_common_setup = {
    "superclass": GitLabBaseServiceController,
    "repository": _repository,
    "start_detector": _start_detector,
    "persistent_error_detector": _persistent_error_detector,
    "ports": _ports,
    "additional_run_settings": {"environment": _environment_variables},
    "service_model": DockerisedServiceWithUsers
}

GitLab8_10_4_ce_0ServiceController = DockerisedServiceControllerTypeBuilder(
    name="GitLab8_10_4_ce_0ServiceController",
    tag="8.10.4-ce.0",
    **_common_setup).build()   # type: type

GitLab8_13_11_ce_0ServiceController = DockerisedServiceControllerTypeBuilder(
    name="GitLab8_13_11_ce_0ServiceController",
    tag="8.13.11-ce.0",
    **_common_setup).build()   # type: type

GitLabServiceController = GitLab8_13_11_ce_0ServiceController

gitlab_service_controllers = {GitLab8_10_4_ce_0ServiceController, GitLab8_13_11_ce_0ServiceController}
