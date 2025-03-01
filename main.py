from qqmusic_api.search import (
    SearchType,
    complete,
    general_search,
    hotkey,
    quick_search,
    search_by_type,
)
from lib import get_credential
from qqmusic_api.song import get_song_urls, EncryptedSongFileType
from qqmusic_api import Session, get_session, singer


async def main():
    async with Session(verify=False):
        credential = await get_credential(3585388545)
        print(await singer.get_mv_list_all("0025NhlN2yWrP4"))


import asyncio

asyncio.run(main())
