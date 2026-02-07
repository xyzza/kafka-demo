import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response

from svc.kafka.producer import AsyncConfluentKafkaProducer, ConfluentProducerConfig
from svc.schemas import PublishRequest


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = ConfluentProducerConfig()
    producer = AsyncConfluentKafkaProducer(config)
    async with producer:
        app.state.producer = producer
        yield


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    @app.put("/publish", status_code=204)
    async def publish(body: PublishRequest, request: Request) -> Response:
        producer: AsyncConfluentKafkaProducer = request.app.state.producer
        topic = os.environ.get("KAFKA_TOPIC", "demo_topic")
        key = str(body.session_id)
        value = body.model_dump(mode="json")
        await producer.send_json(topic, value, key=key)
        return Response(status_code=204)

    return app
