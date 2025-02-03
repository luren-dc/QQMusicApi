"""WEB API Port"""

from datetime import datetime
from enum import Enum
from inspect import Parameter, signature
from typing import Any, Union, get_args, get_origin

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import qqmusic_api

app = FastAPI(
    docs_url=None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.add_exception_handler(
    404,
    lambda request, exc: JSONResponse(
        status_code=404,
        content={"code": 1, "errors": ["Oops! The resource you're looking for was not found."]},
    ),
)


class SkipParse(Exception):
    """跳过解析"""

    pass


class Parser:
    """解析器"""

    def __init__(self, module: str, func: str, params: dict[str, str]):
        self.module = module
        self.func = func
        self.params = params
        self.function = None
        self.valid = True
        self.errors = []

        self.not_allowed_modules = {
            "login",
        }

        self._check_module_permission()

    def _check_module_permission(self):
        """模块权限检查"""
        if self.module in self.not_allowed_modules:
            self.valid = False
            self.errors.append(f"模块 {self.module} 禁止访问")

    def _import_function(self):
        """动态导入模块和函数"""
        if not self.valid:
            return
        try:
            module = getattr(qqmusic_api, self.module)
            try:
                self.function = getattr(module, self.func)
            except AttributeError:
                self.valid = False
                self.errors.append(f"函数 {self.func} 不存在")
        except AttributeError:
            self.valid = False
            self.errors.append(f"模块 {self.module} 不存在")

    async def _parse_params(self) -> dict[str, Any]:
        """根据函数类型注释解析参数"""
        if not self.valid:
            return {}

        if not self.function:
            return {}
        if hasattr(self.function, "api_func"):
            sig = signature(self.function.api_func)
        else:
            sig = signature(self.function)

        parsed_params = {}

        for name, param in sig.parameters.items():
            # 获取参数类型注解
            param_type = param.annotation if param.annotation != Parameter.empty else str
            is_optional = get_origin(param_type) is Union and type(None) in get_args(param_type)

            # 处理可选类型
            if is_optional:
                param_type = next(t for t in get_args(param_type) if t is not type(None))

            # 检查参数是否存在
            if name not in self.params:
                if param.default == Parameter.empty and not is_optional:
                    self.valid = False
                    self.errors.append(f"缺少必填参数: {name}")
                continue

            # 类型转换
            try:
                value = self.params[name]
                parsed_params[name] = self._convert_type(value, param_type)
            except SkipParse:
                continue
            except Exception as e:
                self.valid = False
                self.errors.append(f"参数 {name} 转换失败: {e}")

        return parsed_params

    def _convert_type(self, value: str, target_type: type) -> Any:
        """类型转换逻辑"""
        # 基础类型
        if target_type is str:
            return value
        if target_type is int:
            return int(value)
        if target_type is float:
            return float(value)
        if target_type is bool:
            if value.lower() in ("true", "1", "yes"):
                return True
            if value.lower() in ("false", "0", "no"):
                return False
            raise SkipParse()
        if target_type is datetime:
            return datetime.fromisoformat(value)
        if get_origin(target_type) is list:
            item_type = get_args(target_type)[0]
            return [self._convert_type(item, item_type) for item in value.split(",")]
        if isinstance(target_type, type) and issubclass(target_type, Enum):
            return target_type[value.upper()]
        raise ValueError(f"不支持的类型: {target_type}")

    async def parse(self) -> tuple[Any, list[str]]:
        """执行解析流程"""
        self._import_function()
        if not self.valid:
            return None, self.errors

        parsed_params = await self._parse_params()
        if not self.valid:
            return None, self.errors

        if not self.function:
            return None, self.errors
        try:
            result = await self.function(**parsed_params)
            return result, []
        except Exception as e:
            return None, [f"函数执行错误: {e}"]


async def _api_web(
    request: Request,
    response: Response,
    module: str,
    func: str,
):
    params = dict(request.query_params)
    parser = Parser(module, func, params)
    credential = qqmusic_api.Credential.from_cookies_dict(request.cookies)
    async with qqmusic_api.Session(credential=credential):
        result, errors = await parser.parse()

    if not parser.valid or errors:
        return {"code": 1, "error": errors}
    return {"code": 0, "data": result}


app.add_api_route("/{module}/{func}", _api_web, methods=["GET"])
