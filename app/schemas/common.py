from typing import Literal

from pydantic import BaseModel


class ApiResponse[T](BaseModel):
    status: Literal["OK", "ERROR"] = "OK"
    data: T
