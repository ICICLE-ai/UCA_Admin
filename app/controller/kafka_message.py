import http
from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect, status, concurrency
import asyncio
from pydantic import BaseModel

from app.service.kafka.message_manager import produce_message, consume_message
from app.service.kafka import custom_exceptions

router = APIRouter(
    prefix="/kafka",
    tags=["kafka_message"],
    responses={http.HTTPStatus.NOT_FOUND.value: {"description": "Not found"}},
)


class Message(BaseModel):
    message: dict
    jobId: str


@router.post("/{topic_name}")
async def produce_message_endpoint(topic_name: str, message: Message, request: Request):
    try:
        producer = request.app.state.kafka_producer
        await concurrency.run_in_threadpool(
            lambda: produce_message(
                producer=producer,
                topic=topic_name,
                message=message.message
            ),
        )
        return {"message": f"Message sent to topic '{topic_name}' successfully."}
    except custom_exceptions.TopicNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic '{topic_name}' not found."
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred."
        )

@router.websocket("/ws/{topic_name}")
async def consumer_websocket_endpoint(websocket: WebSocket, topic_name: str):
    shutdown_flag = {"shutdown": False}
    await websocket.accept()

    queue = asyncio.Queue()

    kafka_task = asyncio.create_task(
        concurrency.run_in_threadpool(consume_message, topic_name, queue, shutdown_flag)
    )

    # 연결 상태 모니터링 태스크 추가
    async def monitor_connection():
        """WebSocket 연결 상태를 주기적으로 체크"""
        while not shutdown_flag["shutdown"]:
            try:
                # 짧은 타임아웃으로 receive 시도 - 연결 끊김 감지용
                await asyncio.wait_for(websocket.receive(), timeout=0.1)
            except asyncio.TimeoutError:
                # 타임아웃은 정상 (메시지가 없음)
                continue
            except WebSocketDisconnect:
                print("Connection monitor detected disconnect")
                shutdown_flag["shutdown"] = True
                break
            except Exception as e:
                print(f"Connection monitor error: {e}")
                shutdown_flag["shutdown"] = True
                break

    # 연결 모니터링 태스크 시작
    monitor_task = asyncio.create_task(monitor_connection())

    try:
        while not shutdown_flag["shutdown"]:
            try:
                # 더 짧은 타임아웃 사용
                message = await asyncio.wait_for(queue.get(), timeout=0.5)
                print(f"Sending message to WebSocket: {message}")
                await websocket.send_json(message)
            except asyncio.TimeoutError:
                # queue가 비어있으면 계속 진행
                continue

    except WebSocketDisconnect:
        print("WebSocket disconnected in main loop")
    except Exception as e:
        print(f"WebSocket connection error: {e}")
    finally:
        shutdown_flag["shutdown"] = True
        print("Shutdown flag set to True")

        # 모든 태스크 정리
        monitor_task.cancel()

        if not kafka_task.done():
            kafka_task.cancel()
            try:
                await asyncio.wait_for(kafka_task, timeout=5.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                print("Kafka task cancelled or timed out")

        try:
            await asyncio.wait_for(monitor_task, timeout=1.0)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            print("Monitor task cancelled or timed out")

        print("Cleanup completed")
