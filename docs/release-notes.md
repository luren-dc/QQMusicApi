# Changelog


### Bug 修复
- [769bbfe](https://github.com/luren-dc/QQMusicApi/commit/769bbfeba93df6307587e01cc2fac0d37c98ee3b): MVApi 注释错误 by @luren-dc
- [26929f2](https://github.com/luren-dc/QQMusicApi/commit/26929f26e4f61c5d5f68161cbe360f437ff50820): 修复获取逐字歌词未解析问题 by @luren-dc in [#67](https://github.com/luren-dc/QQMusicApi/pull/67)

### 功能更新
- [40a4cf9](https://github.com/luren-dc/QQMusicApi/commit/40a4cf97e0d2d1ad424fe8cc2ea607fbc43acaca): 支持获取专辑封面链接 by @luren-dc in [#70](https://github.com/luren-dc/QQMusicApi/pull/70)

### 文档更新
- [625685d](https://github.com/luren-dc/QQMusicApi/commit/625685d989bf44697f4903db4144063079260e18): 更新 Readme by @luren-dc
- [a86f4a1](https://github.com/luren-dc/QQMusicApi/commit/a86f4a1d918fae7df8bccb25faab5b0751e91ae4): Update exceptions.md by @luren-dc

### 构建配置
- [b46fa36](https://github.com/luren-dc/QQMusicApi/commit/b46fa36a34820266ce5a3354af36247eca974c44): 更新依赖版本 by @luren-dc

## [0.1.8] - 2024-10-05

### 功能更新
- [02a62f5](https://github.com/luren-dc/QQMusicApi/commit/02a62f57d083b2b5d7c98ad5078ede521c99045d): `get_song_urls` 更好的 Typing Hints by @luren-dc in [#62](https://github.com/luren-dc/QQMusicApi/pull/62)
- [7a99429](https://github.com/luren-dc/QQMusicApi/commit/7a994290cb298a868963d325dccab4a908e5fd9a): 支持 UserApi by @luren-dc in [#59](https://github.com/luren-dc/QQMusicApi/pull/59)
- [3a2b011](https://github.com/luren-dc/QQMusicApi/commit/3a2b011445479327dd433bc934685ac0088b1ef7): 支持检测凭证是否过期 by @luren-dc in [#61](https://github.com/luren-dc/QQMusicApi/pull/61)
- [b8190f5](https://github.com/luren-dc/QQMusicApi/commit/b8190f5663ca6c61ff622f18d0c14d065fe5c38d): 支持在事件循环已经运行时同步执行异步代码 by @luren-dc in [#60](https://github.com/luren-dc/QQMusicApi/pull/60)
- [fe1660e](https://github.com/luren-dc/QQMusicApi/commit/fe1660ed86da7e1bb1bbc05b163af4acfd54205e): 支持 ogg 640kbps 获取 by @luren-dc in [#58](https://github.com/luren-dc/QQMusicApi/pull/58)

### 功能重构
- [11298e9](https://github.com/luren-dc/QQMusicApi/commit/11298e9c3f225b280ad654ab0b63d4c7455dc895): 重构 ApiException by @luren-dc in [#64](https://github.com/luren-dc/QQMusicApi/pull/64)

## [0.1.7] - 2024-09-15

### 功能更新
- [a5534b5](https://github.com/luren-dc/QQMusicApi/commit/a5534b5975bd95e45a5022eafd994362d1046f16): 支持 LyricApi by @luren-dc in [#56](https://github.com/luren-dc/QQMusicApi/pull/56)
- [7d66486](https://github.com/luren-dc/QQMusicApi/commit/7d66486379e8009a60514806d1373f51840010be): 支持获取 OGG 320kbps by @luren-dc in [#55](https://github.com/luren-dc/QQMusicApi/pull/55)
- [bb6cf81](https://github.com/luren-dc/QQMusicApi/commit/bb6cf816a4bb79c5b846e211f4a216b5764dc4de): 支持获取加密和试听文件 by @luren-dc in [#51](https://github.com/luren-dc/QQMusicApi/pull/51)

### 文档更新
- [3bae431](https://github.com/luren-dc/QQMusicApi/commit/3bae4311368f557d3f83e1b34a9efbe84c43b046): 简化贡献文档 by @luren-dc in [#54](https://github.com/luren-dc/QQMusicApi/pull/54)

## [0.1.6] - 2024-08-25

### Bug 修复
- [0afd820](https://github.com/luren-dc/QQMusicApi/commit/0afd820776e117a0d15c282ec8c258c49d0a48e3): 注释错误 by @luren-dc

### 功能更新
- [99fb2d9](https://github.com/luren-dc/QQMusicApi/commit/99fb2d9e4a1468da49f155beb4d08d43e99abccb): 迁移到 httpx by @luren-dc

### 功能重构
- [9e63a1e](https://github.com/luren-dc/QQMusicApi/commit/9e63a1eb4a8cc01a235545c669881b92bafe5868): 重构 Api 代码 by @luren-dc

### 文档更新
- [68c23c3](https://github.com/luren-dc/QQMusicApi/commit/68c23c32dd98596f67bdc91aeea12892680aa49c): 优化贡献文档 by @luren-dc
- [d04053b](https://github.com/luren-dc/QQMusicApi/commit/d04053b13d1776054429f5477a6be3aadeef1d16): 更新贡献指南 by @luren-dc

## [0.1.5] - 2024-08-03

### Bug 修复
- [bc647fa](https://github.com/luren-dc/QQMusicApi/commit/bc647fa9a033bf6f661fb633611293f8c84e40c9): 未使用上下文管理器时报错 by @luren-dc
- [1fc449a](https://github.com/luren-dc/QQMusicApi/commit/1fc449a8c228a8dcc166efd35b84670550c6c2e4): 修复一些小错误 by @luren-dc
- [7963f54](https://github.com/luren-dc/QQMusicApi/commit/7963f547fbfa5bcdcd90c4776d9f1776211f41fa): V0.1.4 未包含库文件 by @luren-dc

### 功能更新
- [d81de7f](https://github.com/luren-dc/QQMusicApi/commit/d81de7f532940ef3e802d36e3341d1b98d1bc63d): 增加对 albumId 的支持 by @luren-dc

### 文档更新
- [a454e21](https://github.com/luren-dc/QQMusicApi/commit/a454e21183277e0ebf7420cbee76bd549c73c7f0): 更新 readme by @luren-dc

## [0.1.4] - 2024-07-28

### 构建配置
- [aad543b](https://github.com/luren-dc/QQMusicApi/commit/aad543b58fe73f46d0eaf6f552dd9a82ad7ca0c5): 更新 pyproject.toml by @luren-dc

## [0.1.3] - 2024-07-27

### 文档更新
- [2f62297](https://github.com/luren-dc/QQMusicApi/commit/2f62297e19de86e5c6ee7f88f0a58efe74cd2d47): 更完善的 API 文档 by @luren-dc in [#38](https://github.com/luren-dc/QQMusicApi/pull/38)

### 构建配置
- [9262b5c](https://github.com/luren-dc/QQMusicApi/commit/9262b5c65ec757329fd729308da28bf47e059951): 迁移依赖管理工具为 PDM by @luren-dc in [#35](https://github.com/luren-dc/QQMusicApi/pull/35)

## [0.1.2] - 2024-07-21

### Bug 修复
- [f188f6e](https://github.com/luren-dc/QQMusicApi/commit/f188f6ef7e034cc3dfef73dd6ab84ad684393fd3): 部分类型错误 by @luren-dc
- [81a00c7](https://github.com/luren-dc/QQMusicApi/commit/81a00c74893b23946d46bcb5854b46f15c3ebd8f): Fatal error on SSL transport by @luren-dc
- [4475513](https://github.com/luren-dc/QQMusicApi/commit/4475513e9849619bb347d3aa776d45cd831707ac): Python3.9 union syntax by @luren-dc
- [eb1fe62](https://github.com/luren-dc/QQMusicApi/commit/eb1fe620afa25d68590002c5311eb368a92ca255): `Api`传入`Credential`无效 by @luren-dc

### 功能更新
- [721546f](https://github.com/luren-dc/QQMusicApi/commit/721546f45022edd819fab11c773962cf1db9c0a8): 添加报错信息，优化二维码获取 by @luren-dc
- [05ea8fe](https://github.com/luren-dc/QQMusicApi/commit/05ea8fec7e780195b89d6354af3bb714d1ebb07a): 更好的错误输出 by @luren-dc
- [218a740](https://github.com/luren-dc/QQMusicApi/commit/218a740136cef98082e840c75a3c4393c2caa0be): 懒获取QIMEI36 by @luren-dc

### 功能重构
- [a44d5ab](https://github.com/luren-dc/QQMusicApi/commit/a44d5ab35c846aa9483bfa76e94838e78fba4fbb): 重构 `LoginApi` 代码 by @luren-dc in [#33](https://github.com/luren-dc/QQMusicApi/pull/33)
- [9b17bf6](https://github.com/luren-dc/QQMusicApi/commit/9b17bf626094376dbfa314c5ac095db396a1e5a7): 重构代码 by @luren-dc in [#22](https://github.com/luren-dc/QQMusicApi/pull/22)

### 性能优化
- [bcdae55](https://github.com/luren-dc/QQMusicApi/commit/bcdae55e61fb7ee52db03643f235fc6a165e0e27): 优化 LoginApi by @luren-dc
- [46a1965](https://github.com/luren-dc/QQMusicApi/commit/46a196566641d199d12fd2540d0d8575fc9ebf41): 优化 TopApi by @luren-dc

### 构建配置
- [3d1dd29](https://github.com/luren-dc/QQMusicApi/commit/3d1dd292e87dd17c5be4e95d5d50ca23b60e40b7): 移除不必要的开发依赖 by @luren-dc

## [0.1.1] - 2024-07-14

### Bug 修复
- [1a36d71](https://github.com/luren-dc/QQMusicApi/commit/1a36d7138c9f21fe13d08e4731922cc68e454cdc): 修改错误注释 by @luren-dc in [#21](https://github.com/luren-dc/QQMusicApi/pull/21)
- [cd72cd7](https://github.com/luren-dc/QQMusicApi/commit/cd72cd7809d371b2b17117c4c78d8eb31a3327cb): Import issue by @luren-dc

### 功能更新
- [b137846](https://github.com/luren-dc/QQMusicApi/commit/b137846ed87d43e15e9078b90203b4e03126d423): Singer API by @luren-dc in [#13](https://github.com/luren-dc/QQMusicApi/pull/13)
- [7959f85](https://github.com/luren-dc/QQMusicApi/commit/7959f85b388e8b3150b2123a229ffa8b6aff6730): 支持 `__repr__` 和 `__str__` by @luren-dc
- [07e7a09](https://github.com/luren-dc/QQMusicApi/commit/07e7a0994ac320d0892f94a6da386684d5c5c7a7): 歌曲Api支持传入Credential by @luren-dc
- [606a163](https://github.com/luren-dc/QQMusicApi/commit/606a1632a6521c34e50c6631f0a0b6de9d292eb8): 增加获取 Album, Singer by @luren-dc
- [506faaa](https://github.com/luren-dc/QQMusicApi/commit/506faaa60f7ec1336dc2532dc4dc2006ed167990): 添加 SingerApi Api by @luren-dc
- [ae00447](https://github.com/luren-dc/QQMusicApi/commit/ae00447e00aec2615781f06a6b421e2e4db77aba): 增加获取歌手列表 API by @luren-dc
- [dd641e5](https://github.com/luren-dc/QQMusicApi/commit/dd641e5b010cb309875903d6ebe7c3aed8d82926): Add Singer API data by @luren-dc

### 性能优化
- [2168c07](https://github.com/luren-dc/QQMusicApi/commit/2168c0795b3f1d2a6ac9b83fbfb11239bdb0241b): 优化获取多个歌曲播放链接性能 by @luren-dc in [#14](https://github.com/luren-dc/QQMusicApi/pull/14)

### 文档更新
- [203c264](https://github.com/luren-dc/QQMusicApi/commit/203c2648b5510d103a58d6a9857b4d392aa2f97f): Update readme by @luren-dc
- [b2d2a8e](https://github.com/luren-dc/QQMusicApi/commit/b2d2a8eecd2a763ca27d94aa222526b7d08c2a8b): 添加 API 文档 by @luren-dc
- [5b72d8d](https://github.com/luren-dc/QQMusicApi/commit/5b72d8da90401644e0224b9c1d9a6dd08eec0c57): 更新 TODO by @luren-dc

## [0.1.0] - 2024-06-07

### Init
- [352c814](https://github.com/luren-dc/QQMusicApi/commit/352c814a79d0ae64714a5d0bcddc353f36ab1b44): 初始化 main 分支 by @luren-dc

### 功能更新
- [6785b4b](https://github.com/luren-dc/QQMusicApi/commit/6785b4b2bc0a729f3291c7b50d6fa35726b6dac2): Add Top API by @luren-dc
- [016f40b](https://github.com/luren-dc/QQMusicApi/commit/016f40b5b3c3f355128275045332cfb9ec0cc864): Add MV API by @luren-dc
- [e827510](https://github.com/luren-dc/QQMusicApi/commit/e827510dc8e3ce2931a90006243dd735adbefefd): Add Album API by @luren-dc
- [5c9b045](https://github.com/luren-dc/QQMusicApi/commit/5c9b04558ea3f32037cec62a019f0c4081796b9d): Add Songlist API by @luren-dc
- [480656e](https://github.com/luren-dc/QQMusicApi/commit/480656e06911267c2ce6f61c5a7f8bb647813e78): Add Login API by @luren-dc
- [6be6382](https://github.com/luren-dc/QQMusicApi/commit/6be638203adc2bc86b6e4b525a4011997174b4f3): Add Song API by @luren-dc
- [7e71614](https://github.com/luren-dc/QQMusicApi/commit/7e71614367995c8e69fa51bdb396f9ae9937ac1f): Add Search API by @luren-dc

### 功能重构
- [40e2c11](https://github.com/luren-dc/QQMusicApi/commit/40e2c11d6f18a73276e2bb675b6a9baabc2f0999): Some functions directly return Class Song by @luren-dc

### 构建配置
- [6320fdb](https://github.com/luren-dc/QQMusicApi/commit/6320fdbf491f926eb9ce673c5349b8638d64ee75): Update pyproject.toml by @luren-dc

<!-- generated by git-cliff -->
