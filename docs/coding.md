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

## 2. 请求流程

### 2.1 `ApiRequest`

```mermaid
%% ApiRequest 流程图
flowchart TD
    A[调用ApiRequest实例] --> B[检查是否传入新Credential]
    B -->|是| C[更新Credential]
    C --> E
    B -->|否| D[保持原有Credential]
    D --> E[生成参数和处理器]
    E --> F{是否启用缓存且存在缓存?}
    F -->|是| G[直接返回缓存数据]
    F -->|否| I[构建请求参数]
    I --> J[发送POST请求]
    J --> K{是否忽略状态码?}
    K -->|否| L[验证HTTP状态码]
    K -->|是| M[跳过状态码验证]
    L --> N[处理响应JSON]
    M --> N
    N --> O{验证业务状态码}
    O -->|0| P[提取数据字段]
    O -->|非0| Q[抛出对应异常]
    P --> R[应用数据处理器]
    R --> S{是否启用缓存?}
    S -->|是| T[保存结果到缓存]
    S -->|否| U[返回结果]
    T --> U
```

### 2.2 `RequestGroup`

```mermaid
%% RequestGroup 流程图
flowchart TD
    A[创建RequestGroup实例] --> B[添加多个ApiRequest]
    B --> C[遍历请求准备参数]
    C --> D[合并公共参数]
    D --> E{是否启用缓存?}
    E -->|是| F[批量检查缓存]
    E -->|否| K[构建合并请求体]
    F --> G[移除已有缓存的请求]
    G --> I{是否有剩余请求?}
    I -->|否| J[直接返回缓存结果]
    I -->|是| K
    K --> L[发送合并POST请求]
    L --> M[解析响应JSON]
    M --> N[遍历子请求处理]
    N --> O{子请求状态码是否正常?}
    O -->|是| P[应用对应处理器]
    O -->|否| Q[抛出异常]
    P --> R{是否启用缓存?}
    R -->|是| S[保存子结果到缓存]
    S --> T
    R -->|否| T[返回完整结果列表]
```
