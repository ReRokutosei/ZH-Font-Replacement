# Yahei-Sarasa

这是一个用于生成改进版微软雅黑和宋体字体的工具。本项目利用更纱黑体(Sarasa Gothic)的优秀 Hinting 机制，将思源黑体(Source Han Sans)与 Segoe UI 结合，生成具有更好显示效果的系统字体替代品。

## 功能特点

- 自动从 GitHub 下载最新版本的更纱黑体
- 支持生成以下字体：
  - 微软雅黑（Regular、Bold、Light）及其 UI 变体
  - 宋体及新宋体（Regular）
  - 宋体扩展（SimSun-ExtB）
  - 等宽编程字体变体（HansCode）
- 保留了 Segoe UI 的高质量 Hinting，提供更清晰锐利的显示效果
- 完整支持中文和英文字符集
- 保持与原版系统字体的兼容性

## 目录结构

```
├── auto_all.py          # 主程序入口，自动执行完整构建流程
├── auto_configs.py      # 全局配置文件
├── fetch_original.py    # 下载更纱黑体源文件
├── generate_fonts.py    # 生成微软雅黑字体
├── generate_simsun.py   # 生成宋体字体
├── rename_code.py       # 处理等宽编程字体
├── rename_segoe.py      # 处理 Segoe UI 字体
├── rename_ttf.py        # 重命名和处理 TTF 文件
└── copy_result.py       # 复制最终结果
```

## 使用方法

1. Windows 用户 FontForge 配置说明
   - 下载并安装 [FontForge Windows 版](https://fontforge.org/en-US/downloads/windows-dl/)
   - 安装后记下安装目录（如 FontForgeBuilds）。
   - 配置 `auto_all.py`
     - 打开 `auto_all.py`，将 `FFPYTHON_PATH` 设置为你的 FontForge 安装路径下的 `bin\\ffpython.exe`，例如：
     - `FFPYTHON_PATH = r"D:\Develop\FontForgeBuilds\bin\ffpython.exe"`
   - 依赖安装
     - 只需在你自己的 Python 环境下用 pip 安装依赖（无需在 FontForge 的 Python 环境下装 pip）。
     - `pip install fonttools requests py7zr wget`
   - 运行主流程
     - 直接用你自己的 Python 运行 `python auto_all.py`，无需用 ffpython 运行主控脚本。   

2. 配置参数（可选）：
   修改 `config.yaml` 文件中的配置项（YAML 格式）：
   ```yaml
   # 源文件下载配置
   HINTED: true
   DOWNLOAD_MODE: local  # local 或 auto
   DOWNLOAD_TIMEOUT: 60
   SOURCE_FILES_DIR: ./source_files

   # 功能开关（至少启用一项）
   ENABLE_MS_YAHEI: true
   ENABLE_SIMSUN: true
   ENABLE_SIMSUN_EXT: true
   ENABLE_HANSCODE: true

   # 字体文件配置
   REGULAR_SOURCE: SarasaUiSC-Regular
   BOLD_SOURCE: SarasaUiSC-Bold
   LIGHT_SOURCE: SarasaUiSC-Light
   EXTRALIGHT_SOURCE: SarasaUiSC-ExtraLight
   SEMIBOLD_SOURCE: SarasaUiSC-SemiBold
   SIMSUN_SOURCE: SarasaUiSC-Regular

   # 基础配置
   COPYRIGHT: Made from sarasa by chenh
   TEMP_DIR: ./temp
   RESULT_DIR: ./result

   # 你想复制的其他文件到结果目录
   OTHER_COPY:
     - SarasaMonoSC-Regular.ttf
     - SarasaMonoSC-Bold.ttf
     - SarasaMonoSC-Italic.ttf
     - SarasaMonoSC-BoldItalic.ttf
   ```
   
   **配置说明：**
   - 所有构建参数均集中在 `config.yaml`，无需手动编辑 py 文件。
   - `DOWNLOAD_MODE` 可选 `local` 或 `auto`，`local` 仅使用本地源文件，`auto` 优先网络下载。
   - 至少启用一项功能开关（如 ENABLE_MS_YAHEI）。
   - 字体源文件名需与 `source_files` 目录下压缩包一致。
   - 其他自定义项可参考注释。

3. 运行构建流程：
   ```bash
   python auto_all.py
   ```

4. 获取生成的字体：
   构建完成后，在 `result` 目录下可以找到以下文件：
   
   微软雅黑系列（当 ENABLE_MS_YAHEI = True）：
   - msyh.ttc - 微软雅黑常规体
   - msyhbd.ttc - 微软雅黑粗体
   - msyhl.ttc - 微软雅黑细体
   - msyhxl.ttc - 微软雅黑极细体
   - msyhsb.ttc - 微软雅黑半粗体
   
   宋体系列：
   - simsun.ttc - 宋体/新宋体（当 ENABLE_SIMSUN = True）
   - simsunb.ttf - 宋体扩展（当 ENABLE_SIMSUN_EXT = True）
   
   编程字体：
   - HansCode-*.ttf - 等宽编程字体（当 ENABLE_HANSCODE = True）
     包含：Regular/Bold/Italic/BoldItalic

## 工作原理

1. 字体处理流程：
   - 下载最新版本的更纱黑体
   - 移除 Segoe UI 中的大部分 OpenType 特性
   - 将 Segoe UI 伪装成 Inter 字体
   - 修改更纱黑体源码，保留 Segoe UI 的 Hinting
   - 构建新的字体文件
   - 修改字体信息，设置正确的字体名称和版权信息

2. 字体特性处理：
   - 移除或保留特定的 OpenType 特性
   - 设置 ClearType 优化
   - 处理 GASP 表
   - 合并字体到 TTC 容器
   - 生成 UI 和非 UI 变体

## 开发计划

1. 提高自动化程度：
   - 简化配置和构建过程
   - 增加错误处理和日志记录
   - 添加构建过程的进度显示

2. 增强功能：
   - 支持输入任意中文字体和拉丁字体
   - 自动优化 Hinting
   - 提供更多字重选项
   - 改进字体特性的处理方式

## 许可证

本项目基于 MIT 许可证开源。详见 [LICENSE](LICENSE) 文件。

## 致谢

- [更纱黑体(Sarasa Gothic)](https://github.com/be5invis/Sarasa-Gothic)
- [思源黑体(Source Han Sans)](https://github.com/adobe-fonts/source-han-sans)
- [Segoe UI](https://learn.microsoft.com/en-us/typography/font-list/segoe-ui)
- [Inter](https://github.com/rsms/inter)

## 注意事项

1. 本项目仅用于学习和研究目的
2. 生成的字体文件仅供个人使用
3. 使用前请确保遵守相关字体的许可条款
4. 不保证生成字体的显示效果与原版系统字体完全一致