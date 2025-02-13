import json
import logging
import time
from collections.abc import Callable
from typing import Any
from uuid import uuid4

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RouterLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, *, logger: logging.Logger) -> None:
        self._logger = logger
        super().__init__(app)

    async def dispatch(self, req: Request, call_next: Callable) -> Response:
        request_id = str(uuid4())
        logging_dict = {"X-API-REQUEST-ID": request_id}

        try:
            res, res_dict = await self._log_response(call_next, req, request_id)
            request_dict = await self._log_request(req)
            logging_dict.update({"request": request_dict, "response": res_dict})
        except Exception as e:
            self._logger.exception(e)
            raise

        self._logger.info(json.dumps(logging_dict))
        return res

    async def _log_request(self, req: Request) -> dict[str, Any]:
        path = req.url.path
        if req.query_params:
            path += f"?{req.query_params}"

        request_logging = {"method": req.method, "path": path, "ip": req.client.host}

        try:
            api_key = req.headers.get("X-API-Key", req.query_params.get("api_key"))
            request_logging["X-API-Key"] = api_key
        except Exception:
            pass

        return request_logging

    async def _log_response(
        self, call_next: Callable, req: Request, req_id: str
    ) -> tuple[Response, dict[str, Any]]:
        start_time = time.perf_counter()
        res = await self._execute_request(call_next, req, req_id)
        execution_time = time.perf_counter() - start_time

        if res:
            res_logging = {
                "status": "successful" if res.status_code < 400 else "failed",
                "status_code": res.status_code,
                "time_taken": f"{execution_time:0.4f}s",
            }
        else:
            res_logging = {"status": "failed", "status_code": 500}
        return res, res_logging

    async def _execute_request(self, call_next: Callable, req: Request, req_id: str) -> Any | None:
        try:
            res = await call_next(req)
            res.headers["X-API-Request-ID"] = req_id
            return res
        except Exception as e:
            self._logger.exception({"path": req.url.path, "method": req.method, "reason": e})
