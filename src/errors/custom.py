class AuthenticationError(Exception):
    def __init__(self):
        super().__init__("Invalid credentials")


class InvalidPasswordConfirmError(Exception):
    def __init__(self):
        super().__init__("Confirm password doesn't match new password")


class UnauthorizedError(Exception):
    def __init__(self):
        super().__init__("User not authorized for this operation")
