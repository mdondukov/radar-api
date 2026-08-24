from typing import Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Schema(BaseModel):
    """Base for schemas exposed over the wire.

    The legacy Kotlin API serialized Kotlin data classes as-is, i.e. camelCase
    (nextStepId, stepId, ...), and calc-web's TypeScript types were written
    against that. populate_by_name keeps snake_case usable from Python code
    (tests, scripts) while the wire format stays camelCase.
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class ApiResponse[T](BaseModel):
    status: Literal["OK", "ERROR"] = "OK"
    data: T
