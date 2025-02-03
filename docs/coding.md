# API 编写指南

## 1. `ApiRequest` 的使用方法

`ApiRequest` 是 QQMusic API 的核心类，用于封装 API 请求。它提供了多种方式来发起请求，以下是几种常见的使用方法：

### 1.1 直接使用 `ApiRequest` 类

你可以直接实例化 `ApiRequest` 类来发起请求。以下是一个简单的示例：

```python
from qqmusicapi.network import ApiRequest
from qqmusicapi.credential import Credential

from typing import Any

async def get_album_detail(album_id: int, credential: Credential):
    req = ApiRequest[[], dict[str, Any]](
        module="music.musichallAlbum.AlbumInfoServer",
        method="GetAlbumDetail",
        params={"albumId": album_id},
        credential=credential,
    )
    response = await req()
    return response
```

在这个示例中，我们创建了一个 `ApiRequest` 实例，指定了模块名、方法名、请求参数和凭证，然后通过 `await req()` 发起请求并获取响应。

### 1.2 使用 `api_request` 装饰器

`api_request` 是一个装饰器，用于简化 API 请求的编写。它可以将一个函数转换为一个返回 `ApiRequest` 实例的函数。以下是一个示例：

```python
from qqmusicapi.network import api_request, NO_PROCESSOR

@api_request("music.musichallAlbum.AlbumInfoServer", "GetAlbumDetail")
async def get_album_detail(value: str | int):
    if isinstance(value, int):
        return {"albumId": value}, NO_PROCESSOR
    return {"albumMId": value}, NO_PROCESSOR
```

在这个示例中，`get_album_detail` 函数被 `api_request` 装饰器修饰，它会自动返回一个 `ApiRequest` 实例。你可以通过 `await get_album_detail(album_id)` 来发起请求。

### 1.3 使用 `RequestGroup` 进行批量请求

`RequestGroup` 用于合并多个 API 请求，支持组级公共参数和重复模块方法处理。以下是一个示例：

```python
from qqmusicapi.network import RequestGroup, ApiRequest

async def get_multiple_album_details(album_ids: list[int], credential: Credential):
    rg = RequestGroup(credential=credential)
    for album_id in album_ids:
        req = ApiRequest(
            module="music.musichallAlbum.AlbumInfoServer",
            method="GetAlbumDetail",
            params={"albumId": album_id},
            credential=credential,
        )
        rg.add_request(req)
    results = await rg.execute()
    return results
```

在这个示例中，我们创建了一个 `RequestGroup` 实例，并将多个 `ApiRequest` 实例添加到其中。通过 `await rg.execute()` 可以一次性发起所有请求，并获取所有请求的结果。

## 2. `api_request` 的原理

`api_request` 装饰器的原理是将一个函数转换为一个返回 `ApiRequest` 实例的函数。它通过以下步骤实现：

1. **定义装饰器**：`api_request` 装饰器接受模块名和方法名作为参数，并返回一个装饰器函数。
2. **包装函数**：装饰器函数会将原始函数包装为一个新的函数，该函数返回一个 `ApiRequest` 实例。
3. **构造请求**：当调用被装饰的函数时，它会根据传入的参数构造 `ApiRequest` 实例，并返回该实例。

通过这种方式，`api_request` 装饰器简化了 API 请求的编写，使得开发者只需关注请求参数的处理，而不需要手动构造 `ApiRequest` 实例。

## 3. `RequestGroup` 的使用

`RequestGroup` 用于合并多个 API 请求，支持组级公共参数和重复模块方法处理。以下是 `RequestGroup` 的主要使用方法：

### 3.1 添加请求

你可以通过 `add_request` 方法将多个 `ApiRequest` 实例添加到 `RequestGroup` 中。每个请求会自动生成一个唯一的键，用于区分不同的请求。

```python
rg = RequestGroup(credential=credential)
req1 = ApiRequest(module="module1", method="method1", params={"param1": "value1"})
req2 = ApiRequest(module="module2", method="method2", params={"param2": "value2"})
rg.add_request(req1)
rg.add_request(req2)
```

### 3.2 执行请求

通过 `execute` 方法可以一次性发起所有请求，并获取所有请求的结果。

```python
results = await rg.execute()
```

`results` 是一个列表，包含了每个请求的响应数据。

### 3.3 处理响应

你可以为每个请求指定一个处理器函数，用于处理响应数据。处理器函数会在请求完成后被调用。

```python
def processor1(data):
    return data["result"]

req1.processor = processor1
```

## 4. `ApiRequest` 的解析

`ApiRequest` 是 QQMusic API 的核心类，负责封装 API 请求的构建、发送和响应处理。它的设计目标是简化 API 请求的编写，同时提供灵活的扩展能力。

### 4.1 `ApiRequest` 的核心功能

`ApiRequest` 的主要功能包括：

- **构建请求参数**：将模块名、方法名、请求参数等封装为 QQMusic API 所需的格式。
- **发送请求**：通过 `httpx` 库发送异步 HTTP 请求。
- **处理响应**：对响应数据进行解析和验证，并根据需要调用处理器函数。

### 4.2 `ApiRequest` 的核心属性

以下是 `ApiRequest` 的核心属性及其作用：

| 属性名           | 类型                              | 说明                                                         |
| ---------------- | --------------------------------- | ------------------------------------------------------------ |
| `module`         | `str`                             | API 模块名，例如 `"music.musichallAlbum.AlbumInfoServer"`。  |
| `method`         | `str`                             | API 方法名，例如 `"GetAlbumDetail"`。                        |
| `params`         | `dict[str, Any]`                  | API 请求的参数。                                             |
| `common`         | `dict[str, Any]`                  | 公共参数，例如 `"cv"`、`"v"`、`"QIMEI36"` 等。               |
| `credential`     | `Credential` 或 `None`            | 用户凭证，用于身份验证。作为函数调用时会获取`credential`参数 |
| `verify`         | `bool`                            | 是否验证凭证的有效性。                                       |
| `ignore_code`    | `bool`                            | 是否忽略响应中的状态码验证。                                 |
| `proceduce_bool` | `bool`                            | 是否将布尔值参数转换为整数（QQMusic API 的特定要求）。       |
| `processor`      | `Callable[[dict[str, Any]], Any]` | 响应处理器函数，用于处理响应数据。                           |

### 4.3 `ApiRequest` 的核心方法

以下是 `ApiRequest` 的核心方法及其作用：

| 方法名               | 说明                                                       |
| -------------------- | ---------------------------------------------------------- |
| `build_request`      | 构建请求参数，包括公共参数、模块参数和签名（如果需要）。   |
| `_process_response`  | 处理响应数据，包括 JSON 解析和状态码验证。                 |
| `_validate_response` | 验证响应状态码，如果状态码异常则抛出相应的异常。           |
| `request`            | 发送异步请求并返回处理后的响应数据。                       |
| `__call__`           | 使 `ApiRequest` 实例可以像函数一样被调用，简化请求的发起。 |

---

## 5. `ApiRequest` 的工作流程

以下是 `ApiRequest` 的工作流程解析：

### 5.1 构建请求参数

当调用 `build_request` 方法时，`ApiRequest` 会执行以下步骤：

1. **构造公共参数**：通过 `_build_common_params` 方法生成公共参数
2. **构造模块参数**：将 `module`、`method` 和 `params` 封装为模块参数。
3. **生成签名**：如果启用了签名（`enable_sign`），则对请求数据进行签名。
4. **返回请求参数**：最终返回一个包含 `url`、`json` 和 `params` 的字典，用于发送请求。

### 5.2 发送请求

当调用 `request` 方法时，`ApiRequest` 会执行以下步骤：

1. **验证凭证**：如果 `verify` 为 `True`，则检查凭证的有效性。
2. **设置 Cookies**：如果凭证有效，则设置请求的 Cookies。
3. **发送请求**：使用 `httpx` 发送异步 POST 请求。
4. **处理响应**：调用 `_process_response` 方法处理响应数据。

### 5.3 处理响应

当调用 `_process_response` 方法时，`ApiRequest` 会执行以下步骤：

1. **解析 JSON**：将响应内容解析为 JSON 格式。
2. **提取数据**：从响应中提取与当前模块和方法对应的数据。
3. **验证状态码**：如果 `ignore_code` 为 `False`，则调用 `_validate_response` 方法验证状态码。
4. **返回数据**：返回处理后的数据。

### 5.4 验证状态码

当调用 `_validate_response` 方法时，`ApiRequest` 会检查响应中的状态码：

- 如果状态码为 `0`，表示请求成功。
- 如果状态码为 `2000`，表示签名无效，抛出 `SignInvalidError`。
- 如果状态码为 `1000`，表示凭证过期，抛出 `CredentialExpiredError`。
- 如果状态码为其他值，抛出 `ResponseCodeError`。

## 6. `RequestGroup` 的工作流程解析

`RequestGroup` 用于批量管理多个 `ApiRequest`，并将它们合并成一个请求以提高效率。以下是 `RequestGroup` 的详细工作流程：

### 6.1 添加请求

在 `RequestGroup` 中，每个 `ApiRequest` 通过 `add_request` 方法被添加到 `_requests` 列表，并为其分配一个唯一的键。

步骤

1. 生成请求的唯一键：key = "{module}.{method}",若同一 module.method 被多次添加，则追加一个计数器，如 "music.vkey.GetVkey.1"。
2. 将 `ApiRequest` 副本及其处理函数 `processor` 存入 `_requests` 列表。

```python
rg = RequestGroup()
req1 = ApiRequest("music.vkey.GetVkey", "UrlGetVkey", params={"songmid": ["123"]})
req2 = ApiRequest("music.vkey.GetVkey", "UrlGetVkey", params={"songmid": ["456"]})

rg.add_request(req1)
rg.add_request(req2)  # 这个请求的 key 会变成 "music.vkey.GetVkey.1"
```

### 6.2 构建合并请求

`build_request` 方法会遍历 `_requests` 列表，合并所有请求数据，并添加公共参数。

1. **生成公共参数**：调用 `_build_common_params` 获取 `Session` 的全局公共参数。
2. **遍历请求列表**：若 `ApiRequest` 绑定了 `api_func`，则先执行 `api_func` 以获取 `params` 和 `processor`。更新 `params` 并存入 `merged_data`。
3. **返回最终请求参数**：组合公共参数与所有请求的 `params`，生成最终请求的 `url`、`json` 数据，若启用了签名 (`enable_sign`)，则计算 `sign` 并添加到 `params`。

### 6.3 发送请求

`execute` 方法用于实际发送请求并获取结果。

1. 调用 `build_request` 生成最终请求数据。
2. 设置 Cookies（若请求涉及凭证）。
3. 使用 `httpx` 发送 POST 请求。
4. 调用 `_process_response` 解析响应数据。

### 6.4 解析响应

`_process_response` 负责处理 `httpx.Response` 并提取对应的 `ApiRequest` 结果。

1. **解析 JSON**：若 `resp.content` 为空，返回 []。解析 JSON 数据，遍历 `_requests` 列表。
2. **根据 key 获取每个请求的响应数据**：`req_data = data.get(req_item["key"], {})`
3. **验证响应状态码**：调用 `_validate_response` 检查 code 是否为 0。
4. **调用 processor 处理数据**：`req_item["processor"](req_data.get("data", req_data))`
