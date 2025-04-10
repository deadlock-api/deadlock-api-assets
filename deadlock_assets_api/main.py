import logging.config
import os
import sys

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from scalar_fastapi import get_scalar_api_reference
from starlette.middleware.gzip import GZipMiddleware
from starlette.requests import Request
from starlette.responses import FileResponse, RedirectResponse, Response
from starlette.staticfiles import StaticFiles
from starlette.status import HTTP_308_PERMANENT_REDIRECT

from deadlock_assets_api.logging_middleware import RouterLoggingMiddleware
from deadlock_assets_api.routes import raw, v1, v2

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "DEBUG"))
logging.config.dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "%(asctime)s %(process)s %(levelname)s %(name)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "level": os.environ.get("LOG_LEVEL", "DEBUG"),
                "class": "logging.StreamHandler",
                "stream": sys.stderr,
            }
        },
        "root": {"level": "DEBUG", "handlers": ["console"], "propagate": True},
    }
)
logging.getLogger("boto3").setLevel(logging.WARNING)
logging.getLogger("botocore").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("clickhouse_driver").setLevel(logging.WARNING)

LOGGER = logging.getLogger(__name__)

if "SENTRY_DSN" in os.environ:
    import sentry_sdk

    sentry_sdk.init(
        dsn=os.environ["SENTRY_DSN"],
        traces_sample_rate=0.2,
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

app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)
app.add_middleware(RouterLoggingMiddleware, logger=LOGGER)


@app.middleware("http")
async def cors_handler(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


Instrumentator(should_group_status_codes=False).instrument(app).expose(app, include_in_schema=False)

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
        response.headers["Cache-Control"] = f"public, max-age={7 * 24 * 60 * 60}"
    return response


class StaticFilesCache(StaticFiles):
    def file_response(self, *args, **kwargs) -> Response:
        resp: Response = super().file_response(*args, **kwargs)
        resp.headers.setdefault(
            "Cache-Control",
            f"public, max-age={7 * 24 * 60 * 60}, s-maxage={7 * 24 * 60 * 60}, immutable",
        )
        return resp


app.mount("/images", StaticFilesCache(directory="images"), name="images")
app.mount("/videos", StaticFilesCache(directory="videos"), name="videos")
app.mount("/icons", StaticFilesCache(directory="svgs"), name="svgs")
app.mount("/sounds", StaticFilesCache(directory="sounds"), name="sounds")


@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse("/scalar", HTTP_308_PERMANENT_REDIRECT)


@app.get("/health", include_in_schema=False)
def get_health():
    return {"status": "ok"}


@app.get("/favicon.ico", include_in_schema=False)
def get_favicon():
    return FileResponse("favicon.ico")


@app.get("/robots.txt", include_in_schema=False)
def get_robots() -> str:
    return """
User-agent: *
Disallow: /
Allow: /docs
Allow: /scalar
Allow: /openapi.json
    """


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
