import math
from datetime import date, datetime
from enum import Enum
from typing import Optional, List, Dict
from pydantic import (
    BaseModel, EmailStr, HttpUrl, Field, validator, root_validator
)


class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    NON_BINARY = "NON_BINARY"


class Address(BaseModel):
    street_address: str
    postal_code: str
    city: str
    country: str


class Person1(BaseModel):
    first_name: str
    last_name: str
    age: int


class Person2(BaseModel):
    first_name: str
    last_name: str
    gender: Gender
    birthdate: date
    interests: List[str]


class Person3(BaseModel):
    first_name: str
    last_name: str
    gender: Gender
    birthdate: date
    interests: List[str]
    address: Address


class UserProfile(BaseModel):
    nickname: str
    location: Optional[str] = None
    subscribed_newsletter: bool = True


class ModelWithBadDefaults(BaseModel):
    # Don't do this.
    d: datetime = datetime.now()


class Person4(BaseModel):
    first_name: str = Field(..., min_length=3)
    last_name: str = Field(..., min_length=3)
    age: Optional[int] = Field(None, ge=0, le=120)


def list_factory():
    return ["a", "b", "c"]


class ModelWithGoodDefaults(BaseModel):
    l: List[str] = Field(default_factory=list_factory)
    d: datetime = Field(default_factory=datetime.now)
    l2: List[str] = Field(default_factory=list)


class User1(BaseModel):
    email: EmailStr
    website: HttpUrl


class Person5(BaseModel):
    first_name: str
    last_name: str
    birthdate: date

    @validator("birthdate") # Specify the field to be validated
    def valid_birthdate(cls, field: date): # Class method!!
        delta = date.today() - field
        age = delta.days / 365
        if age > 120:
            # In case of errors, raise exception of 'ValueError' type
            raise ValueError("You seem a bit too old!") 
        # In case of success, return the modified field value    
        return f"Your age is {math.floor(age)}" 


class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    password_confirmation: str

    @root_validator()
    def passwords_match(cls, values): # The 'values' dict contain the object fields
        password = values.get("password")
        password_confirmation = values.get("password_confirmation")
        if password != password_confirmation:
            # In case of errors, raise exception of 'ValueError' type
            raise ValueError("Passwords don't match")
        # In case of success, return the modified 'values' dict
        return values


class ModelWithEarlyValidation(BaseModel):
    values: List[int]

    @validator("values", pre=True)
    def split_string_values(cls, v):
        if isinstance(v, str):
            return v.split(",")
        return v


class Person6(BaseModel):
    first_name: str
    last_name: str
    gender: Gender
    birthdate: date
    interests: List[str]
    address: Address

    def name_dict(self):
        return self.dict(include={"first_name", "last_name"})


class PostBase(BaseModel):
    title: str
    content: str


class PostPartialUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class PostCreate(PostBase):
    pass


class PostPublic(PostBase):
    id: int


class PostDB(PostBase):
    id: int
    nb_views: int = 0


class DummyDatabase:
    posts: Dict[int, PostDB] = {}


