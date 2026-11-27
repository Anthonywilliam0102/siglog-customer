class DomainError(Exception):
    """Erro de regra de negócio. `status` sugere o código HTTP ao traduzir na API."""

    status = 422

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFound(DomainError):
    status = 404


class Forbidden(DomainError):
    status = 403


class Conflict(DomainError):
    status = 409
