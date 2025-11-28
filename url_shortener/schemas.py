from pydantic import BaseModel


class LinkSchema(BaseModel):
    slug: str
    url: str
