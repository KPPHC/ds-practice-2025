from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Book(_message.Message):
    __slots__ = ("bookId", "book_quantity")
    BOOKID_FIELD_NUMBER: _ClassVar[int]
    BOOK_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    bookId: str
    book_quantity: str
    def __init__(self, bookId: _Optional[str] = ..., book_quantity: _Optional[str] = ...) -> None: ...

class TransactionVerificationRequest(_message.Message):
    __slots__ = ("user_books", "user_name", "user_email", "card_number", "card_expiry", "card_cvv", "billing_street", "billing_city", "billing_state", "billing_zip", "shipping_method", "terms_accepted")
    USER_BOOKS_FIELD_NUMBER: _ClassVar[int]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    USER_EMAIL_FIELD_NUMBER: _ClassVar[int]
    CARD_NUMBER_FIELD_NUMBER: _ClassVar[int]
    CARD_EXPIRY_FIELD_NUMBER: _ClassVar[int]
    CARD_CVV_FIELD_NUMBER: _ClassVar[int]
    BILLING_STREET_FIELD_NUMBER: _ClassVar[int]
    BILLING_CITY_FIELD_NUMBER: _ClassVar[int]
    BILLING_STATE_FIELD_NUMBER: _ClassVar[int]
    BILLING_ZIP_FIELD_NUMBER: _ClassVar[int]
    SHIPPING_METHOD_FIELD_NUMBER: _ClassVar[int]
    TERMS_ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    user_books: _containers.RepeatedCompositeFieldContainer[Book]
    user_name: str
    user_email: str
    card_number: str
    card_expiry: str
    card_cvv: str
    billing_street: str
    billing_city: str
    billing_state: str
    billing_zip: str
    shipping_method: str
    terms_accepted: bool
    def __init__(self, user_books: _Optional[_Iterable[_Union[Book, _Mapping]]] = ..., user_name: _Optional[str] = ..., user_email: _Optional[str] = ..., card_number: _Optional[str] = ..., card_expiry: _Optional[str] = ..., card_cvv: _Optional[str] = ..., billing_street: _Optional[str] = ..., billing_city: _Optional[str] = ..., billing_state: _Optional[str] = ..., billing_zip: _Optional[str] = ..., shipping_method: _Optional[str] = ..., terms_accepted: bool = ...) -> None: ...

class TransactionVerificationResponse(_message.Message):
    __slots__ = ("is_valid", "reason")
    IS_VALID_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    is_valid: bool
    reason: str
    def __init__(self, is_valid: bool = ..., reason: _Optional[str] = ...) -> None: ...
