"""This router is used to get the images"""
from fastapi import APIRouter, Response

from prisma import get_client
from prisma.models import Image

router = APIRouter(tags=["Images"])


@router.get("/images", summary="Get Images", response_model_exclude_none=True)
def get_images() -> list[Image]:
    """Get all images"""
    db = get_client()
    images = db.image.find_many()
    for image in images:
        del image.data
    return images


@router.get(
    "/images/{image_name}",
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
def get_image(image_name: str) -> Response:
    """Get specific image"""
    db = get_client()
    image_data = db.image.find_first(where={"name": image_name}).data.decode()
    return Response(content=image_data, media_type="image/png")
