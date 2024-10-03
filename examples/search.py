# --8<-- [start:import]
from qqmusic_api import search, sync

# --8<-- [end:import]

# --8<-- [start:search_by_type]
sync(
    search.search_by_type(
        "周杰伦",
        search_type=search.SearchType.SINGER,
        page=1,
        highlight=False,
    )
)
# --8<-- [end:search_by_type]

# --8<-- [start:general_search]
sync(
    search.general_search(
        "周杰伦",
        page=1,
        highlight=False,
    )
)
# --8<-- [end:general_search]

# --8<-- [start:quick_search]
sync(
    search.quick_search(
        "周杰伦",
    )
)
# --8<-- [end:quick_search]
