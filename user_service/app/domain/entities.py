import enum


class UserRole(str, enum.Enum):
    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"
