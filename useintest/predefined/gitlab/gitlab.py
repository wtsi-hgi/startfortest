from abc import ABCMeta

from useintest.services.models import User, DockerisedServiceWithUsers
from useintest.services._builders import DockerisedServiceControllerTypeBuilder
from useintest.services.controllers import DockerisedServiceController, ServiceType

ROOT_USERNAME = "root"
ROOT_PASSWORD = "gitlab123"

_repository = "gitlab/gitlab-ce"
_ports = [80, 433, 22]
_start_detector = lambda log_line: "==> /var/log/gitlab/redis/current <==" in log_line
_persistent_error_detector = lambda log_line: "o space left on device" in log_line
_environment_variables = {"GITLAB_ROOT_PASSWORD": ROOT_PASSWORD}


class GitLabBaseServiceController(DockerisedServiceController[ServiceType], metaclass=ABCMeta):
    """
    Base class for GitLab service controllers.
    """
    def start_service(self) -> DockerisedServiceWithUsers:
        service = super().start_service()
        service.root_user = User(ROOT_USERNAME, ROOT_PASSWORD)
        return service


common_setup = {
    "superclass": GitLabBaseServiceController,
    "repository": _repository,
    "start_detector": _start_detector,
    "persistent_error_detector": _persistent_error_detector,
    "ports": _ports,
    "additional_run_settings": {"environment": _environment_variables}
}

GitLab8_10_4_ce_0ServiceController = DockerisedServiceControllerTypeBuilder(
    name="GitLab8_10_4_ce_0ServiceController",
    tag="8.10.4-ce.0",
    **common_setup).build()

GitLab8_13_11_ce_0ServiceController = DockerisedServiceControllerTypeBuilder(
    name="GitLab8_13_11_ce_0ServiceController",
    tag="8.13.11-ce.0",
    **common_setup).build()

GitLab8_16_6_ce_0ServiceController = DockerisedServiceControllerTypeBuilder(
    name="GitLab8_16_6_ce_0ServiceController",
    tag="8.16.6-ce.0",
    **common_setup).build()

GitLab10_0_3_ce_0ServiceController = DockerisedServiceControllerTypeBuilder(
    name="GitLab10_0_3_ce_0ServiceController",
    tag="10.0.3-ce.0",
    **common_setup).build()


GitLabServiceController = GitLab10_0_3_ce_0ServiceController

gitlab_service_controllers = {GitLab8_10_4_ce_0ServiceController, GitLab8_13_11_ce_0ServiceController,
                              GitLab8_16_6_ce_0ServiceController, GitLab10_0_3_ce_0ServiceController}
