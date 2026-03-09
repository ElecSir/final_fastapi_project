from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

from .books import ReturnedBook


__all__ = [
    "IncomingSeller",
    "ReturnedSeller",
    "ReturnedSellerWithBooks",
    "ReturnedAllSellers",
]


# Базовый класс "Продавец", содержащий поля, которые есть во всех классах-наследниках.
class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    e_mail: str


# Класс для валидации входящих данных
class IncomingSeller(BaseSeller):
    password: str

    @field_validator("e_mail")
    @staticmethod
    def validate_email(val: str):
        if "@" not in val:
            raise PydanticCustomError("Validation error", "Invalid email!")
        return val

    @field_validator("password")
    @staticmethod
    def validate_password(val: str):
        if len(val) < 10:
            raise PydanticCustomError("Validation error", "Password must be at least 10 characters long!")
        return val


# Класс, валидирующий исходящие данные
class ReturnedSeller(BaseSeller):
    id: int


# Класс для возврата продавца + его книги
class ReturnedSellerWithBooks(ReturnedSeller):
    books: list[ReturnedBook]


# Класс для возврата массива объектов "Продавец"
class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]