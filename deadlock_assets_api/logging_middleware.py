import json
import logging
import time
from collections.abc import Callable
from typing import Any

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RouterLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, *, logger: logging.Logger) -> None:
        self._logger = logger
        super().__init__(app)

    async def dispatch(self, req: Request, call_next: Callable) -> Response:
        try:
            res, res_dict = await self._log_response(call_next, req)
            request_dict = await self._log_request(req)
            self._logger.info(json.dumps({"request": request_dict, "response": res_dict}))
            return res
        except Exception as e:
            self._logger.exception(e)
            raise

    async def _log_request(self, req: Request) -> dict[str, Any]:
        path = req.url.path
        if req.query_params:
            path += f"?{req.query_params}"
        return {"path": path}

    async def _log_response(
        self, call_next: Callable, req: Request
    ) -> tuple[Response, dict[str, Any]]:
        start_time = time.perf_counter()
        res = await self._execute_request(call_next, req)
        execution_time = time.perf_counter() - start_time

        if res:
            res_logging = {
                "status_code": res.status_code,
                "method": req.method,
                "time_taken": f"{execution_time:0.4f}s",
            }
        else:
            res_logging = {"status_code": 500}
        return res, res_logging

    async def _execute_request(self, call_next: Callable, req: Request) -> Any | None:
        try:
            return await call_next(req)
        except Exception as e:
            self._logger.exception({"path": req.url.path, "method": req.method, "reason": e})
