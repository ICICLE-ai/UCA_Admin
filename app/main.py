from fastapi import FastAPI
from app.lifespan import lifespan
from app.controller import kafka_topic, kafka_message

app = FastAPI(
    swagger_ui_parameters={"syntaxHighlight": {"theme": "obsidian"}},
    lifespan=lifespan,
)

app.include_router(kafka_topic.router)
app.include_router(kafka_message.router)


async def root():
    return {"message": "Hello World"}
