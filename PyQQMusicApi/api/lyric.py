from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from qqmusic import QQMusic


class LyricApi:
    parent: ClassVar[QQMusic]
