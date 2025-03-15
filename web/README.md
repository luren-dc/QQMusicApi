# Web Port 使用说明

## 1. 安装与运行

### 克隆仓库

```bash
git clone https://github.com/luren-dc/QQMusicApi
```

### 依赖安装

```bash
uv sync --group web
```

### 启动服务

```bash
uv run uvicorn web.app:app --host 0.0.0.0 --port 8000 --reload
```

### Docker

```bash
docker build . -t qq-music-api
docker run -d -p 8000:8000 qq-music-api
```

## 2. API Endpoint

- **请求格式**: `GET /{module}/{func}`
- **示例**:  
  `GET /song/get_detail?id=12345`

## 3. 请求参数规则

### 类型转换规则

| 参数类型    | 示例值                          | 说明                                 |
| ----------- | ------------------------------- | ------------------------------------ |
| `int`       | `count=5`                       | 整数                                 |
| `bool`      | `is_vip=true`                   | `true`/`1`/`yes` 或 `false`/`0`/`no` |
| `datetime`  | `date=2023-10-01T12:34`         | ISO 8601 格式                        |
| `list[int]` | `id=1,2,3`                      | 逗号分隔的字符串                     |
| `Enum`      | `type=SongType.HIT`or`type=HIT` | 枚举名或值（见具体模块定义）         |
