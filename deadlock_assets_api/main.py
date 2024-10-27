import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.gzip import GZipMiddleware
from starlette.requests import Request
from starlette.responses import FileResponse, RedirectResponse, Response
from starlette.staticfiles import StaticFiles

from deadlock_assets_api.routes import base, raw, v1, v2

logging.basicConfig(level=logging.INFO)

if "SENTRY_DSN" in os.environ:
    import sentry_sdk

    sentry_sdk.init(
        dsn=os.environ["SENTRY_DSN"],
        traces_sample_rate=1.0,
        _experiments={
            "continuous_profiling_auto_start": True,
        },
    )

app = FastAPI(
    title="Assets - Deadlock API",
    description="""
Part of the [https://deadlock-api.com](https://deadlock-api.com) project.

API for Deadlock assets, including hero stats and images, and item stats and images.

_deadlock-api.com is not endorsed by Valve and does not reflect the views or opinions of Valve or anyone officially involved in producing or managing Valve properties. Valve and all associated properties are trademarks or registered trademarks of Valve Corporation_
""",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)

Instrumentator(should_group_status_codes=False).instrument(app).expose(
    app, include_in_schema=False
)

app.include_router(base.router, include_in_schema=False)
app.include_router(v2.router)
app.include_router(v1.router)
app.include_router(raw.router)


@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    response = await call_next(request)
    if "Cache-Control" in response.headers:
        return response

    is_success = 200 <= response.status_code < 300
    is_docs = request.url.path.replace("/", "").startswith("docs")
    is_health = request.url.path.replace("/", "").startswith("health")
    if is_success and not is_docs and not is_health:
        response.headers["Cache-Control"] = "public, max-age=86400"
    return response


class StaticFilesCache(StaticFiles):
    def file_response(self, *args, **kwargs) -> Response:
        resp: Response = super().file_response(*args, **kwargs)
        resp.headers.setdefault(
            "Cache-Control", "public, max-age=604800, s-maxage=604800, immutable"
        )
        return resp


app.mount("/images", StaticFilesCache(directory="images"), name="images")
app.mount("/videos", StaticFilesCache(directory="videos"), name="videos")
app.mount("/icons", StaticFilesCache(directory="svgs"), name="svgs")


@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse("/docs")


@app.get("/health", include_in_schema=False)
def get_health():
    return {"status": "ok"}


@app.get("/favicon.ico", include_in_schema=False)
def get_favicon():
    return FileResponse("favicon.ico")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
