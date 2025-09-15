# app/domain/errors.py

class EmailAlreadyExists(Exception):
    """Aynı email ile kullanıcı kayıtlıysa fırlatılır."""
    pass


class InvalidCredentials(Exception):
    """Login sırasında email/şifre yanlışsa fırlatılır."""
    pass


class UserNotFound(Exception):
    """Kullanıcı bulunamazsa fırlatılır."""
    pass
