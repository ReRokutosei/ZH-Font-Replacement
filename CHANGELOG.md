#  (2025-07-01)


* refactor(core)!: 精简重构字体生成与主流程 ([13efa5a](https://github.com/ReRokutosei/yahei-sarasa/commit/13efa5a3551355768b7bf9fac13f875f930c6f59))


### Bug Fixes

* **auto_all:** HansCode 编程字体输出到正确的结果子目录 ([bdaaec3](https://github.com/ReRokutosei/yahei-sarasa/commit/bdaaec37369b5a5131dd0f26a392a181c2325c9e))
* **config:** 修复 OTHER_COPY 配置项为 None 时异常，FFPYTHON_PATH 强制从 yaml 读取 ([1d3b060](https://github.com/ReRokutosei/yahei-sarasa/commit/1d3b06094e6a7064237db870d207f3b978b0f29e))
* **copy_result:** 自动复制 HansCode-*.ttf 编程字体到结果目录 ([75837ba](https://github.com/ReRokutosei/yahei-sarasa/commit/75837bab9fbab26f023af04f1f6616bad938793f))


### Features

* **automation:** 自动化拆分与主流程重构，修正字重与压缩包处理 ([32c7de4](https://github.com/ReRokutosei/yahei-sarasa/commit/32c7de403b11510813f339ef5cd015ca2fb691ef))
* **config,build,docs:** 支持更多字重、可选流程与本地源兜底，提升自动化与文档指引 ([7a7081a](https://github.com/ReRokutosei/yahei-sarasa/commit/7a7081aa07eb6ba01837f14274e949f4d1faed6b))
* **version:** 生成的所有字体Version字段自动添加当前日期 ([0867d88](https://github.com/ReRokutosei/yahei-sarasa/commit/0867d8817e2aaf8b7e843c36df406892fa4496e6))


### BREAKING CHANGES

* - 改为依赖 config.yaml 配置
- 目录结构和部分行为更为自动化，
* **automation:** - Windows 用户需手动指定 FFPYTHON_PATH，且只需在主控环境 pip 安装依赖
* **config,build,docs:** - 需根据新配置文件格式调整 auto_configs.py
- 需在 source_files 目录手动放置字体包以支持本地兜底
- 依赖包和本地源文件准备方式有重大简化，用户无需再下载体积巨大的 Sarasa-TTF-*.7z



#  (2025-06-29)


* refactor(core)!: 精简重构字体生成与主流程 ([13efa5a](https://github.com/ReRokutosei/yahei-sarasa/commit/13efa5a3551355768b7bf9fac13f875f930c6f59))


### Bug Fixes

* **config:** 修复 OTHER_COPY 配置项为 None 时异常，FFPYTHON_PATH 强制从 yaml 读取 ([1d3b060](https://github.com/ReRokutosei/yahei-sarasa/commit/1d3b06094e6a7064237db870d207f3b978b0f29e))


### Features

* **automation:** 自动化拆分与主流程重构，修正字重与压缩包处理 ([32c7de4](https://github.com/ReRokutosei/yahei-sarasa/commit/32c7de403b11510813f339ef5cd015ca2fb691ef))
* **config,build,docs:** 支持更多字重、可选流程与本地源兜底，提升自动化与文档指引 ([7a7081a](https://github.com/ReRokutosei/yahei-sarasa/commit/7a7081aa07eb6ba01837f14274e949f4d1faed6b))


### BREAKING CHANGES

* - 改为依赖 config.yaml 配置
- 目录结构和部分行为更为自动化，
* **automation:** - Windows 用户需手动指定 FFPYTHON_PATH，且只需在主控环境 pip 安装依赖
* **config,build,docs:** - 需根据新配置文件格式调整 auto_configs.py
- 需在 source_files 目录手动放置字体包以支持本地兜底
- 依赖包和本地源文件准备方式有重大简化，用户无需再下载体积巨大的 Sarasa-TTF-*.7z



