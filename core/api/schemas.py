from typing import Optional

from ninja import Schema


class BlogPostIn(Schema):
    title: str
    description: str = ""
    slug: str
    tags: str = ""
    content: str
    icon: Optional[str] = None  # URL or base64 string
    image: Optional[str] = None  # URL or base64 string


class BlogPostOut(Schema):
    status: str
    message: str
