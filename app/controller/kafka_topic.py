import http
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel
from app.service.kafka.topic_manager import create_topic, remove_topic, list_topics
from app.service.kafka import custom_exceptions

router = APIRouter(
    prefix="/kafka_admin",
    tags=["kafka_topic"],
    responses={http.HTTPStatus.NOT_FOUND.value: {"description": "Not found"}},
)


@router.get("/list-topics")
async def list_topics_endpoint(request: Request):
    try:
        admin_client = request.app.state.kafka_admin_client
        return list_topics(admin_client)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred."
        )


class TopicModel(BaseModel):
    topic: str
    description: str = None
    associated_projects: list = []


@router.post("/create-topic")
async def create_topic_endpoint(topic: TopicModel, request: Request):
    try:
        admin_client = request.app.state.kafka_admin_client
        create_topic(admin_client, topic.topic)
        # todo: store topic metadata in a database: no rush
        return {"message": f"Topic '{topic.topic}' created."}
    except custom_exceptions.TopicAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic '{topic}' already exists."
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred."
        )


@router.delete("/delete-topic")
async def delete_topic_endpoint(topic: str, request: Request):
    try:
        admin_client = request.app.state.kafka_admin_client
        remove_topic(admin_client, topic)
        return {"message": f"Topic '{topic}' deleted."}
    except custom_exceptions.TopicNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic '{topic}' not found."
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred."
        )
