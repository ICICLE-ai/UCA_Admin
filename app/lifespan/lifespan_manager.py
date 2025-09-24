from contextlib import asynccontextmanager
from fastapi import FastAPI
from .kafka_manager import connect_kafka, disconnect_kafka

@asynccontextmanager
async def lifespan(app: FastAPI):
    connect_kafka(app)
    yield
    disconnect_kafka(app)