"""WEB API Port (完整优化版)"""

from time import time
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel

import qqmusic_api
from web.parser import Parser


class ApiResponseModel(BaseModel):
    """API响应数据模型"""

    code: int
    message: str
    data: Any = None
    errors: list[str] | None = None
    timestamp: int


class ApiResponse(ORJSONResponse):
    """标准化API响应类"""

    def __init__(
        self,
        status_code: int = status.HTTP_200_OK,
        message: str = "Success",
        data: Any = None,
        errors: str | list[str] | None = None,
        **kwargs,
    ):
        # 错误信息标准化处理
        processed_errors = None
        if errors:
            processed_errors = [errors] if isinstance(errors, str) else errors

        # 构建响应内容
        content = ApiResponseModel(
            code=status_code, message=message, data=data, errors=processed_errors, timestamp=int(time())
        ).dict(exclude_unset=True, exclude_defaults=True)

        super().__init__(content=content, status_code=status_code, **kwargs)

    @classmethod
    def success(
        cls, data: Any = None, message: str = "Success", status_code: int = status.HTTP_200_OK
    ) -> "ApiResponse":
        """构建成功响应"""
        return cls(status_code=status_code, message=message, data=data)

    @classmethod
    def error(
        cls, errors: str | list[str], message: str = "Error", status_code: int = status.HTTP_400_BAD_REQUEST
    ) -> "ApiResponse":
        """构建错误响应"""
        return cls(status_code=status_code, message=message, errors=errors)


app = FastAPI(
    title="QQMusic API",
    description="QQMusic API Web Port",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    default_response_class=ApiResponse,  # 设置默认响应类
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.exception_handler(404)
async def _not_found_handler(request: Request, exc: HTTPException):
    return ApiResponse.error(errors="请求的资源不存在", message="Not Found", status_code=status.HTTP_404_NOT_FOUND)


@app.exception_handler(500)
async def _server_error_handler(request: Request, exc: HTTPException):
    return ApiResponse.error(
        errors=["服务器内部错误"], message="Internal Server Error", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


@app.exception_handler(422)
async def _validation_error_handler(request: Request, exc: HTTPException):
    return ApiResponse.error(
        errors=["参数验证失败"], message="Validation Error", status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


async def _api_web(
    request: Request,
    module: str,
    func: str,
):
    """统一API请求处理"""
    try:
        # 凭证处理
        credential = qqmusic_api.Credential.from_cookies_dict(request.cookies)
        qqmusic_api.get_session().credential = credential
    except Exception:
        return ApiResponse.error(
            errors="无效的用户凭证", message="Unauthorized", status_code=status.HTTP_401_UNAUTHORIZED
        )

    # 参数解析
    params = dict(request.query_params)
    parser = Parser(module, func, params)

    # 执行解析
    try:
        result, errors = await parser.parse()
    except Exception:
        return ApiResponse.error(
            errors=["服务器处理请求时发生异常"],
            message="Internal Error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # 错误处理
    if errors:
        return ApiResponse.error(
            errors=errors, message="Request Validation Failed", status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    if not parser.valid:
        return ApiResponse.error(
            errors=["无效的请求参数"], message="Bad Request", status_code=status.HTTP_400_BAD_REQUEST
        )

    # 成功响应
    return ApiResponse.success(data=result, message="请求成功")


app.add_api_route(
    path="/{module}/{func}",
    endpoint=_api_web,
    methods=["GET"],
    responses={
        200: {"model": ApiResponseModel},
        400: {"model": ApiResponseModel},
        401: {"model": ApiResponseModel},
        422: {"model": ApiResponseModel},
        500: {"model": ApiResponseModel},
    },
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="debug",
    )
