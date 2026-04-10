from ..model.requests import ChangePasswordRequest
from ..model.responses import ChangePasswordResponse


def change_password(request: ChangePasswordRequest) -> ChangePasswordResponse:
    return ChangePasswordResponse(message="")
