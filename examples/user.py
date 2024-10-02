# --8<-- [start:import]
from qqmusic_api import Credential, sync, user

musicid = 0
musickey = ""

credential = Credential(musicid=musicid, musickey=musickey)
# --8<-- [end:import]

# --8<-- [start:get_euin]
sync(user.get_euin(2680888327, credential))
# --8<-- [end:get_euin]

# --8<-- [start:user]
u = user.User("owCFoecFNeoA7z**", credential)

# 获取主页信息
sync(u.get_homepage())

# 获取收藏歌单
sync(u.get_fav_songlist())

# 获取用户歌单
sync(u.get_created_songlist())
# --8<-- [end:user]

# --8<-- [start:my]
# 获取自己账号信息
my = user.User(sync(user.get_euin(credential.musicid, credential)), credential)

# 或者 credential.encrypt_uin 不为空
# my = user.User(credential.encrypt_uin, credential)

# 获取好友
# 只根据传入的 credential 获取
sync(my.get_friend())
# --8<-- [end:my]
