import asyncio

import httpx

from qqmusic_api import Credential, song

MUSICID = 0
MUSICKEY = ""

credential = Credential(musicid=MUSICID, musickey=MUSICKEY)

# 会员歌曲需登录
urls = asyncio.run(song.get_song_urls(mid=["003w2xz20QlUZt", "000Zu3Ah1jb4gl"], credential=credential))


async def download_file(client, mid, url):
    try:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            # 文件名 {mid}.mp3
            file_path = f"{mid}.mp3"
            with open(file_path, "wb") as f:
                async for chunk in response.aiter_bytes(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        print(f"Downloaded {file_path}")
    except httpx.RequestError as e:
        print(f"An error occurred: {e}")


async def main():
    async with httpx.AsyncClient() as client:
        tasks = [download_file(client, mid, url) for mid, url in urls.items() if url]
        await asyncio.gather(*tasks)


asyncio.run(main())
