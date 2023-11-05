import argparse
import asyncio

import requests

from pyqqmusicapi import QQMusic
from pyqqmusicapi.utils import search_song

parser = argparse.ArgumentParser()
parser.add_argument("--id", type=int, default=0, help="歌单ID")

api = QQMusic()


async def download_playlist(id: int):
    data = await api.playlist.detail(id)
    info = data["info"]
    print(
        "歌单信息：",
        f"歌单标题：{info['title']}",
        f"歌单创建者：{info['creator']['nick']}",
        f"歌单含有歌曲：{info['songnum']}",
        sep="\n",
    )
    if info["songnum"]:
        mids = [song["info"]["mid"] for song in data["list"]]
        urls = await api.song.url(mids, urltype="play")
        for mid, url in urls.items():
            song = search_song(data["list"], mid)
            if url:
                await download_song(song["info"]["title"], url)
            else:
                print(song["info"]["title"], "未获取到下载链接")
    print("下载完成")


async def download_song(filename: str, url: str):
    data = requests.get(url, stream=True)
    with open(filename + ".mp3", "wb") as file:
        for chunck in data.iter_content(chunk_size=1024):
            file.write(chunck)


async def main():
    id = int(input("请输入歌单ID"))
    await download_playlist(id)


if __name__ == "__main__":
    args = parser.parse_args()
    if args.id:
        asyncio.run(download_playlist(args.id))
    else:
        asyncio.run(main())
