from uuid import UUID

from pydantic import BaseModel


class PublishRequest(BaseModel):
    session_id: UUID
    files: list[str]
    location: tuple[float, float]
