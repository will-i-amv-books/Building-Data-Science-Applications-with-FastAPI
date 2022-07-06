from typing import Dict, Optional
from pydantic import BaseModel


class Post(BaseModel):
    id: int
    title: str
    content: str


class PostUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]


class DummyDatabase:
    posts: Dict[int, Post] = {}
