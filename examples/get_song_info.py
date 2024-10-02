from qqmusic_api import song, sync

s = song.Song(mid="001CJxVG1yppB0")
# song.Song(id=105648974)

mid = sync(s.get_id())
id = sync(s.get_mid())

# 获取基本信息
info = sync(s.get_info())

# 获取详细信息
detail = sync(s.get_detail())
