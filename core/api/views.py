from django.http import HttpRequest
from ninja import NinjaAPI

from core.api.auth import MultipleAuthSchema
from core.api.schemas import BlogPostIn, BlogPostOut
from core.models import BlogPost
from isitketo.utils import get_isitketo_logger

logger = get_isitketo_logger(__name__)


api = NinjaAPI(auth=MultipleAuthSchema())


@api.post("/blog-posts/submit", response=BlogPostOut, include_in_schema=False)
def submit_blog_post(request: HttpRequest, data: BlogPostIn):
    user = getattr(request, "auth", None)
    if not user or not getattr(user, "is_superuser", False):
        return BlogPostOut(status="error", message="Forbidden: superuser access required."), 403
    try:
        BlogPost.objects.create(
            title=data.title,
            description=data.description,
            slug=data.slug,
            tags=data.tags,
            content=data.content,
        )
        logger.info("Blog post submitted successfully.", user=user.username, blog_post=data.title)
        return BlogPostOut(status="success", message="Blog post submitted successfully.")
    except Exception as e:
        return BlogPostOut(status="error", message=f"Failed to submit blog post: {str(e)}")
