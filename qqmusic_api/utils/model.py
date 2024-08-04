"""模型数据"""

from pydantic import BaseModel, Field, field_validator


class SongFileInfo(BaseModel):
    """歌曲文件信息

    Attributes:
        media_mid: 媒体 id
        size_new: 臻品等新类型大小
        size_flac: FLAC 大小
        size_128mp3: 128kbps MP3 大小
        size_320mp3: 320kbps MP3 大小
        size_48aac: 48kbps AAC 大小
        size_96aac: 96kbps AAC 大小
        size_192aac: 192kbps AAC 大小
        size_96ogg: 96kbps OGG 大小
        size_192ogg: 192kbps OGG 大小
        size_try: 试听大小
        try_begin: 试听起始时间
        try_end: 试听结束时间
    """

    media_mid: str = ""
    size_new: list[int] = []
    size_flac: int = 0
    size_128mp3: int = 0
    size_320mp3: int = 0
    size_48aac: int = 0
    size_96aac: int = 0
    size_192aac: int = 0
    size_96ogg: int = 0
    size_192ogg: int = 0
    size_try: int = 0
    try_begin: int = 0
    try_end: int = 0


class AlbumInfo(BaseModel):
    """专辑信息

    Attributes:
        id: 专辑 id
        mid: 专辑 mid
        name: 专辑名
        title: 专辑标题
        subtitle: 专辑副标题
        time_public: 发行时间
    """

    id: int = 0
    mid: str = ""
    name: str = ""
    title: str = ""
    subtitle: str = ""
    time_public: str = ""


class SingerInfo(BaseModel):
    """歌手信息

    Attributes:
        id: 歌手 id
        mid: 歌手 mid
        name: 歌手名
    """

    id: int = 0
    mid: str = ""
    name: str = ""


class MVInfo(BaseModel):
    """MV 信息

    Attributes:
        id: mv id
        vid: mv id
        name: mv 名称
        title: mv 标题
    """

    id: int = 0
    vid: str = ""
    name: str = ""
    title: str = ""


class PayInfo(BaseModel):
    """付费信息

    Attributes:
        pay_down: 是否付费下载
        pay_month: 是否包月下载
        pay_play: 是否付费播放
        pay_status: 付费状态
        price_album: 专辑价格（单位：分）
        price_track: 歌曲价格（单位：分）
        time_free: 是否限时免费
    """

    pay_down: int = 0
    pay_month: int = 0
    pay_play: int = 0
    pay_status: int = 0
    price_album: int = 0
    price_track: int = 0
    time_free: int = 0


class SongInfo(BaseModel):
    """歌曲信息

    Attributes:
        id: 歌曲 id
        mid: 歌曲 mid
        name: 歌曲名
        title: 歌曲标题
        subtitle: 歌曲副标题
        desc: 歌曲描述
        language: 歌曲语种
        time_public: 发行时间
        pay: 付费信息
        file: 歌曲文件信息
        album: 专辑信息
        singer: 歌手信息
        grp: 相似歌曲
        vs: 试听文件 media_mid
    """

    id: int = 0
    mid: str = ""
    name: str = ""
    title: str = ""
    subtitle: str = ""
    desc: str = ""
    language: int = 0
    time_public: str = ""
    pay: PayInfo = Field(default_factory=PayInfo)
    file: SongFileInfo = Field(default_factory=SongFileInfo)
    album: AlbumInfo = Field(default_factory=AlbumInfo)
    singer: list[SingerInfo] = []
    grp: list["SongInfo"] = []
    vs: str = ""

    @field_validator("vs", mode="before")
    @classmethod
    def _get_vs(cls, values: list[str]) -> str:
        return values[0]


class SongDetailObject(BaseModel):
    """歌曲详情对象

    Attributes:
        title: 标题
        type: 类型
        content: 内容
    """

    title: str = ""
    type: str = ""
    content: list[dict] = []


class SongDetail(BaseModel):
    """歌曲详情

    Attributes:
        company: 发行公司
        genre: 类型
        intro: 简介
        lan: 语言
        pub_time: 发行时间
        extras: 额外信息
        track_info: 歌曲信息
    """

    company: SongDetailObject = Field(default_factory=SongDetailObject)
    genre: SongDetailObject = Field(default_factory=SongDetailObject)
    intro: SongDetailObject = Field(default_factory=SongDetailObject)
    lan: SongDetailObject = Field(default_factory=SongDetailObject)
    pub_time: SongDetailObject = Field(default_factory=SongDetailObject)
    extras: dict = Field(default_factory=dict)
    track_info: SongInfo = Field(default_factory=SongInfo)


class SongLabel(BaseModel):
    """歌曲标签

    Attributes:
        id: 标签 id
        text: 标签文本
        icon: 标签图标
        url: 标签链接
        type: 标签类型
        species: 标签种类
    """

    id: int = 0
    text: str = Field(default="", alias="tagTxt")
    icon: str = Field(default="", alias="tagIcon")
    url: str = Field(default="", alias="tagUrl")
    type: int = 0
    species: int = 0


class RelatedPlaylist(BaseModel):
    """相关歌单

    Attributes:
        id: 歌单 id
        title: 歌单标题
        cover: 歌单封面
        creator: 歌单创建者
        song_num: 歌单歌曲数
    """

    id: int = Field(default=0, alias="tid")
    title: str = ""
    cover: str = ""
    creator: str = ""
    song_num: int = Field(default=0, alias="songNum")


class RelatedMV(BaseModel):
    """相关MV

    Attributes:
        vid: vid
        mvid: mvid
        title: mv 标题
        singer: mv 歌手
        playcnt: mv 播放次数
        cover: mv 封面
    """

    vid: str = ""
    mvid: int = 0
    title: str = ""
    singer: list[SingerInfo] = Field(default=list, alias="singers")
    playcnt: int = 0
    cover: str = Field(default="", alias="picurl")


class RelatedSheet(BaseModel):
    """相关曲谱

    Attributes:
        mid: 曲谱 id
        name: 曲谱名称
        url: 曲谱链接
        type: 曲谱类型
        str_type: 曲谱类型文本
        cover: 曲谱封面
        pic: 曲谱图片
        version: 曲谱版本
        uploader: 曲谱上传者
        song_mid: 歌曲 id
        ins_type: 乐器类型
        str_ins_type: 乐器类型文本
    """

    mid: str = Field(default="", alias="scoreMID")
    name: str = Field(default="", alias="scoreName")
    url: str = ""
    type: int = Field(default=0, alias="scoreType")
    str_type: str = Field(default="", alias="strScoreType")
    cover: str = Field(default="", alias="coverURL")
    pic: list[str] = Field(default_factory=list, alias="picURLs")
    version: str = ""
    uploader: str = ""
    song_mid: str = Field(default="", alias="songMID")
    ins_type: int = Field(default=0, alias="insType")
    str_ins_type: str = Field(default="", alias="strInsType")


class ProducerInfo(BaseModel):
    """制作者信息

    Attributes:
        type: 类型
        name: 名称
        icon: 图标
        scheme: 链接
        singer_mid: 歌手 id
        follow: 是否关注
    """

    type: int = Field(default=0, alias="Type")
    name: str = Field(default="", alias="Name")
    icon: str = Field(default="", alias="Icon")
    scheme: str = Field(default="", alias="Scheme")
    singer_mid: str = Field(default="", alias="SingerMid")
    follow: int = Field(default=0, alias="Follow")


class ProducerObject(BaseModel):
    """制作者对象

    Attributes:
        title: 标题
        producers: 制作人
        type: 类型
    """

    title: str = Field(default="", alias="Title")
    producers: list[ProducerInfo] = Field(default=list, alias="Producers")
    type: int = Field(default=0, alias="Type")
