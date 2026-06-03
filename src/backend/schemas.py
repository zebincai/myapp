from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class UserPayload(BaseModel):
    name: NonEmptyString
    age: int = Field(ge=0)
    job: NonEmptyString


class UserCreate(UserPayload):
    pass


class UserUpdate(UserPayload):
    pass


class UserRead(UserPayload):
    id: int

    model_config = ConfigDict(from_attributes=True)
