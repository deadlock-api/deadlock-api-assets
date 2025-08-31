import logging.config
import os
import sys

from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference, Theme
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
logging.getLogger("urllib3").setLevel(logging.WARNING)

LOGGER = logging.getLogger(__name__)

app = FastAPI(
    title="Assets - Deadlock API",
    servers=[{"url": "https://assets.deadlock-api.com"}],
    description="""
## Support the Deadlock API

Whether you're building your own database, developing data science projects, or enhancing your website with game and player analytics, the Deadlock API has the data you need.

Your sponsorship helps keep this resource open, free and future-proof for everyone. By supporting the Deadlock API, you will enable continued development, new features and reliable access for developers, analysts and streamers worldwide.

Help us continue to provide the data you need - sponsor the Deadlock API today!

**-> You can Sponsor the Deadlock API on [Patreon](https://www.patreon.com/c/user?u=68961896) or [GitHub](https://github.com/sponsors/raimannma)**

## Disclaimer
_deadlock-api.com is not endorsed by Valve and does not reflect the views or opinions of Valve or anyone officially involved in producing or managing Valve properties. Valve and all associated properties are trademarks or registered trademarks of Valve Corporation_
""",
    license_info={
        "name": "MIT",
        "url": "https://github.com/deadlock-api/deadlock-api-assets/blob/master/LICENSE",
    },
    contact={"name": "Deadlock API - Discord", "url": "https://discord.gg/XMF9Xrgfqu"},
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
        response.headers["Cache-Control"] = (
            f"public, max-age={24 * 60 * 60}, s-maxage={60 * 60}, stale-while-revalidate={24 * 60 * 60}, stale-if-error={24 * 60 * 60}"
        )
    return response


class StaticFilesCache(StaticFiles):
    def file_response(self, *args, **kwargs) -> Response:
        resp: Response = super().file_response(*args, **kwargs)
        resp.headers.setdefault(
            "Cache-Control",
            f"public, max-age={24 * 60 * 60}, s-maxage={60 * 60}, stale-while-revalidate={24 * 60 * 60}",
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


@app.head("/health", include_in_schema=False)
def get_health_head():
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
        openapi_url="https://assets.deadlock-api.com/openapi.json",
        title=app.title,
        theme=Theme.ALTERNATE,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0")
