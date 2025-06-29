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

1. 需要安装以下 Python 依赖：
   
   ```sh
   pip install fonttools fontforge requests py7zr wget
   ```
   

2. 配置参数（可选）：
   修改 `auto_configs.py` 文件中的配置项：
   ```python
   # 下载设置
   HINTED = True           # 是否使用 Hinted 版本的更纱黑体
   DOWNLOAD_MODE = 'auto'  # 'auto'-优先网络下载，失败时使用本地文件；'local'-仅使用本地文件
   DOWNLOAD_TIMEOUT = 60   # 下载超时时间（秒）
   
   # 功能开关（至少启用一项）
   ENABLE_MS_YAHEI = True    # 是否生成微软雅黑字体
   ENABLE_SIMSUN = True      # 是否生成宋体
   ENABLE_SIMSUN_EXT = True  # 是否生成宋体扩展
   ENABLE_HANSCODE = True    # 是否生成等宽编程字体
   
   # 字体文件配置
   REGULAR_SOURCE = 'SarasaUiSC-Regular'    # 标准字体文件名
   BOLD_SOURCE = 'SarasaUiSC-Bold'          # 粗体文件名
   LIGHT_SOURCE = 'SarasaUiSC-Light'        # 细体文件名
   XLIGHT_SOURCE = 'SarasaUiSC-ExtraLight'  # 极细体文件名
   SEMIBOLD_SOURCE = 'SarasaUiSC-SemiBold'  # 半粗体文件名
   SIMSUN_SOURCE = 'SarasaUiSC-Regular'     # 宋体文件名
   ```
   
   **字体源文件说明：**
   1. 如果在`auto_configs.py`选择`local`模式，则需要从[等距更纱仓库](https://github.com/be5invis/Sarasa-Gothic/releases/latest)准备如下四个目标压缩包：
      - SarasaUiSC-TTF-<version>.7z
      - SarasaUiSC-TTF-Unhinted-<version>.7z
      - SarasaMonoSC-TTF-<version>.7z
      - SarasaMonoSC-TTF-Unhinted-<version>.7z
   2. 将下载的压缩包放置在根目录 `source_files` 目录下
   3. 在线下载模式，程序会自动优先选择最新版本和优先级最高的包
   4. 无需下载体积巨大的 Sarasa-TTF-*.7z 或其它无关包

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