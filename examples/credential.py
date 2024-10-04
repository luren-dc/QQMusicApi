from qqmusic_api import Credential, sync

credential = Credential()

# 判断能否刷新 credential
# 不代表能刷新成功
sync(credential.can_refresh())

# 判断 credential 是否过期
sync(credential.is_expired())

# 刷新 credential
sync(credential.refresh())
