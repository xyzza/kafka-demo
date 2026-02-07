from fastapi import FastAPI, Response

from svc.schemas import PublishRequest


def create_app() -> FastAPI:
    app = FastAPI()

    @app.put("/publish", status_code=204)
    async def publish(body: PublishRequest) -> Response:
        return Response(status_code=204)

    return app
