"""代码解析"""

import types
from datetime import datetime
from enum import Enum
from inspect import Parameter, signature
from typing import Any, Union, get_args, get_origin

import qqmusic_api
from qqmusic_api.exceptions import ApiException


class Parser:
    """请求参数解析器"""

    def __init__(self, module: str, func: str, params: dict[str, str]):
        self.module = module
        self.func = func
        self.params = params
        self.function = None
        self.valid = True
        self.errors = []

        # 禁止访问的模块
        self.not_allowed_modules = ["login"]

    def _check_module_permission(self):
        """检查模块访问权限"""
        if self.module in self.not_allowed_modules:
            self.valid = False
            self.errors.append(f"模块 {self.module} 禁止访问")

    def _import_function(self):
        """导入模块和函数"""
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
        """解析请求参数"""
        if not self.valid or not self.function:
            return {}

        # 获取函数签名
        if hasattr(self.function, "api_func"):
            sig = signature(self.function.api_func)
        else:
            sig = signature(self.function)

        parsed_params = {}
        for name, param in sig.parameters.items():
            try:
                parsed_value = self._parse_parameter(name, param)
                if parsed_value is not None:
                    parsed_params[name] = parsed_value
            except ValueError as e:  # noqa: PERF203
                self.valid = False
                self.errors.append(str(e))

        return parsed_params

    def _parse_parameter(self, name: str, param: Parameter) -> Any | None:
        """解析单个参数"""
        # 获取参数类型
        param_type = param.annotation if param.annotation != Parameter.empty else str
        is_optional = get_origin(param_type) is Union and type(None) in get_args(param_type)

        # 处理可选类型
        if is_optional:
            param_type = next(t for t in get_args(param_type) if t is not type(None))

        # 检查参数是否存在
        if name not in self.params:
            if param.default == Parameter.empty and not is_optional:
                raise ValueError(f"缺少必填参数: {name}")
            return None

        # 类型转换
        value = self.params[name]
        try:
            return self._convert_type(value, param_type)
        except Exception as e:
            raise ValueError(f"参数 {name} 转换失败: {e}")

    def _convert_type(self, value: str, target_type: type) -> Any:  # noqa: C901
        """类型转换逻辑"""
        origin = get_origin(target_type)
        args = get_args(target_type)

        if origin is Union or origin is types.UnionType:
            errors = []
            for subtype in args:
                try:
                    return self._convert_type(value, subtype)
                except ValueError as e:  # noqa: PERF203
                    errors.append(str(e))
            allowed_types = ", ".join([st.__name__ if hasattr(st, "__name__") else str(st) for st in args])
            raise ValueError(
                f"值 '{value}' 无法转换为联合类型中的任一类型: {allowed_types}。错误详情: {', '.join(errors)}"
            )

        if target_type is str:
            return value
        if target_type is int:
            try:
                return int(value)
            except ValueError as e:
                raise ValueError(f"值 '{value}' 无法转换为整数") from e
        if target_type is float:
            try:
                return float(value)
            except ValueError as e:
                raise ValueError(f"值 '{value}' 无法转换为浮点数") from e
        if target_type is bool:
            lower_val = value.lower()
            if lower_val in ("true", "1", "yes", "on"):
                return True
            if lower_val in ("false", "0", "no", "off"):
                return False
            raise ValueError(f"值 '{value}' 无法转换为布尔类型")
        if target_type is datetime:
            try:
                return datetime.fromisoformat(value)
            except ValueError as e:
                raise ValueError(f"值 '{value}' 不符合ISO 8601格式") from e
        if origin is list:
            item_type = args[0]
            try:
                return [self._convert_type(item.strip(), item_type) for item in value.split(",")]
            except Exception as e:
                raise ValueError(f"列表转换失败: {e!s}") from e
        if issubclass(target_type, Enum):
            if "." in value:
                type_str = value.split(".")[0]
                value = value.split(".")[1]
                if type_str != target_type.__name__:
                    raise ValueError(f"不匹配的枚举类型: {target_type}")
            upper_val = value.upper()
            for member in target_type:
                if member.name.upper() == upper_val:
                    return member
            for member in target_type:
                if str(member.value) == value:
                    return member
            allowed = [f"{m.name.lower()} ({m.value})" for m in target_type]
            raise ValueError(f"值 '{value}' 无效,允许的枚举值为:{', '.join(allowed)}")
        raise ValueError(f"不支持的类型: {target_type}")

    async def parse(self) -> tuple[Any, list[str]]:
        """执行解析流程"""
        self._check_module_permission()
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
        except ApiException as e:
            return None, [f"QQ音乐API错误: {e}"]
        except Exception as e:
            return None, [f"函数执行错误: {e}"]
