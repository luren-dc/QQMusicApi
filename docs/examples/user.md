# 用户

```python
from qqmusic_api import Credential, sync, user

musicid = 0
musickey = ""

credential = Credential(musicid=musicid, musickey=musickey)
```

## 示例：获取 musicid

```python
sync(user.get_musicid("owCFoecFNeoA7z**"))
```

## 示例：获取 euin

```python
sync(user.get_euin(2680888327))
```

## 示例：获取用户信息

```python
u = user.User("owCFoecFNeoA7z**")

# 部分 API 需要有效 `credential`,否则报错
u = user.User("owCFoecFNeoA7z**", credential)

# 获取主页信息
sync(u.get_homepage())

# 获取收藏歌单
sync(u.get_fav_songlist())

# 获取用户歌单
sync(u.get_created_songlist())

# 获取自己账号信息
my = user.User(sync(user.get_euin(credential.musicid)), credential)

# 或者 credential.encrypt_uin 不为空
# my = user.User(credential.encrypt_uin, credential)

# 获取好友
# 只根据传入的 credential 获取
sync(my.get_friend())
```
