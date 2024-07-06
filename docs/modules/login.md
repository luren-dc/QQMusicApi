# Module login.py

```python
from qqmusic_api import login
```

登录操作类

## class QrCodeLoginEvents

**Extends:** enum.Enum

二维码登录状态

+ SCAN: 未扫描二维码
+ CONF: 未确认登录
+ TIMEOUT: 二维码过期
+ DONE: 成功
+ REFUSE: 拒绝登录
+ OTHER: 未知情况

## class PhoneLoginEvents

**Extends:** enum.Enum

手机登录状态

+ SEND: 发送成功
+ CAPTCHA: 需要滑块验证
+ OTHER: 未知情况

## class Login

登录抽象类

### \_\_init\_\_()

初始化登录类

### async def get_qrcode()

获取二维码

**Returns:** bytes: 二维码图像数据

### async def get_qrcode_state()

获取二维码状态

**Returns:** QrCodeLoginEvents: 二维码状态

### async def authorize()

登录鉴权

| name | type | description |
| - | - | - |
| authcode | Optional[int] | 验证码. Defaults to None |

**Returns:** Credential: 用户凭证

### async def send_authcode()

发送验证码

**Returns:** PhoneLoginEvents: 操作状态

## class QQLogin

QQ登录类

### async def get_qrcode()

获取二维码

**Returns:** bytes: 二维码图像数据

### async def get_qrcode_state()

获取二维码状态

**Returns:** QrCodeLoginEvents: 二维码状态

### async def authorize()

登录鉴权

| name | type | description |
| - | - | - |
| authcode | Optional[int] | 验证码. Defaults to None |

**Returns:** Credential: 用户凭证

## class WXLogin

微信登录类

### async def get_qrcode()

获取二维码

**Returns:** bytes: 二维码图像数据

### async def get_qrcode_state()

获取二维码状态

**Returns:** QrCodeLoginEvents: 二维码状态

### async def authorize()

登录鉴权

| name | type | description |
| - | - | - |
| authcode | Optional[int] | 验证码. Defaults to None |

**Returns:** Credential: 用户凭证

## class PhoneLogin

手机号登录类

### \_\_init\_\_()

| name | type | description |
| - | - | - |
| phone | int | 手机号码 |

### async def send_authcode()

发送验证码

**Returns:** PhoneLoginEvents: 操作状态

### async def authorize()

登录鉴权

| name | type | description |
| - | - | - |
| authcode | Optional[int] | 验证码. Defaults to None |

**Returns:** Credential: 用户凭证

## async def refresh_cookies()

刷新 Cookies

| name | type | description |
| - | - | - |
| credential | Credential | 用户凭证 |

**Returns:** Credential: 新的用户凭证
