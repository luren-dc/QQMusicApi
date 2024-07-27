# API 文档

## QQ音乐 API

<div class="grid cards" markdown>

-   :material-album: **[album]** - 专辑信息 API

    ***

    - 详细信息
    - 专辑歌曲

-   :material-login: **[login]** - 账号登录 API

    ***

    - QQ 登录
    - 微信登录
    - 手机号登录

-   :material-magnify: **[search]** - 搜索 API

    ***

    - 热搜词
    - 搜索词补全
    - 快速搜索
    - 综合搜索
    - 类型搜索

-  :material-music-circle: **[song]** - 歌曲信息 API

    ***

    - 详细信息
    - 相似歌曲
    - 歌曲标签
    - 相关歌单
    - 相关MV
    - 其他版本
    - 相关曲谱
    - 制作信息
    - 歌曲文件链接

-  :material-video: **[mv]** - MV 信息 API

    ***

    - 详细信息
    - 相关歌曲
    - 播放链接

-  :material-microphone: **[singer]** - 歌手信息 API

    ***

    - 歌手列表
    - 主页信息

-   :material-view-list: **[songlist]** - 歌单信息 API

    ***

    - 详细信息
    - 歌单歌曲

-   :material-sort: **[top]** - 排行榜 API

    ***

    - 排行榜列表
    - 排行榜信息
    - 排行榜歌曲

</div>

  [album]: album.md
  [login]: login.md
  [mv]: mv.md
  [search]: search.md
  [singer]: singer.md
  [song]: song.md
  [songlist]: songlist.md
  [top]: top.md

## 辅助模块

<div class="grid cards" markdown>

-   :octicons-verified-16: **[qimei]** - 识别标识

    ***

    获取设备唯一标识

-   :material-tools: **[utils]** - 实用程序

    ***

    辅助函数

-   :material-network: **[network]** - 网络请求

    ***

    请求 API 核心

-   :material-cookie: **[credential]** - 凭据管理

    ***

    用于管理请求 API 时的 cookies

-   :material-sync: **[sync]** - 同步执行函数

    ***

    同步执行异步代码函数(仅用于同步程序)

</div>

  [qimei]: utils/qimei.md
  [utils]: utils/utils.md
  [network]: utils/network.md
  [credential]: utils/credential.md
  [sync]: utils/sync.md
