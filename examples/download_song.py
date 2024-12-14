import asyncio

import anyio
import httpx

from qqmusic_api import Credential, song

MUSICID = 0
MUSICKEY = ""

credential = Credential(musicid=MUSICID, musickey=MUSICKEY)

# 会员歌曲需登录
urls = asyncio.run(song.get_song_urls(mid=["003w2xz20QlUZt", "000Zu3Ah1jb4gl"], credential=credential))

# 获取加密文件
# 可在 https://um-react.netlify.app/ 解密
# urls = asyncio.run(
#     song.get_song_urls(
#         mid=["003w2xz20QlUZt", "000Zu3Ah1jb4gl"], credential=credential, file_type=song.EncryptedSongFileType.FLAC
#     )
# )


async def download_file(client, mid, url):
    try:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            # 文件名 {mid}.mp3
            file_path = f"{mid}.mp3"
            async with await anyio.open_file(file_path, "wb") as f:
                async for chunk in response.aiter_bytes(1024 * 5):
                    if chunk:
                        await f.write(chunk)
        print(f"Downloaded {file_path}")
    except httpx.RequestError as e:
        print(f"An error occurred: {e}")


async def main():
    async with httpx.AsyncClient() as client:
        tasks = [download_file(client, mid, url) for mid, url in urls.items() if url]
        await asyncio.gather(*tasks)


asyncio.run(main())
