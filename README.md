# ZH-Font-Replacement

## 背景

在最近的一次Windows更新后，系统UI字体意外地恢复到了~~丑丑的~~默认的微软雅黑字体。在此之前，我使用的是"等距更纱黑体替换微软雅黑"方案，该方案源自一位大佬基于更纱黑体所做的改进。我记得这位大佬原帖发在某乎上：`等距更纱完美替换微软雅黑，且生效全部5个字重及斜体（提供非等距版）`，但现在有关的搜索结果是某度知道上的相关回答。尽管原作者分享的文件仍然保存在我的本地，但考虑到更纱黑体可能已经经历了多次更新，我需要更新版本的替换包。

一番查找后，目前存在多种解决方案：从功能强大的工具如`No!! MeiryoUI`到各种大佬精心制作的成品，发布时间也各有不同。这些方案似乎都不太符合我的需求。在搜索过程中，我注意到了项目[yahei-sarasa](https://github.com/chenh96/yahei-sarasa)，该项目通过Github API获取最新版本的更纱黑体来构建微软雅黑字体，这一思路给了我很大启发。于是，我fork了这个项目并进行了相应的修改。但在后续实践中发现偏离预期效果，并且原项目使用FontForge，在Windows环境调用不是很方便，于是我决定彻底重写，并解除fork关系。

在这个过程中，我提取了原版微软雅黑的NAME(中英)元信息存储为json~~我不喜欢XML~~，并借鉴了之前提到的“等距更纱完美替换微软雅黑”方案，补充了额外的斜体元数据（虽然不确定是否必要）。具体来说，原版msyh.ttc只包含两个常规的ttf，我增加了2个对应的斜体。

目前项目只是简单地做了改写元数据的工作，因为我不会具体的字形优化。

## 项目简介

本项目用于追踪最新版本Release，自动生成**替换** Windows 10/11 的默认字体文件（微软雅黑、Segoe UI）。

## 主要功能

-   基于 **更纱黑体** 生成微软雅黑字体文件。
-   基于 **Inter** 生成Segoe UI字体文件。
-   可自定义其他字体包作为生成基础。


## 重要须知

> [!CAUTION]
> 字体替换存在风险，请确保具备相关知识和实操能力
> 
> 本项目生成的文件**仅限用于开发与测试环境**。
> 
> **严禁在生产环境或日常中使用！**
> 
> 
> **本项目不提供替换教程或自动化替换功能。**
>
>  **你需要自行查找教程并手动替换**系统的原始字体文件。


- [ZH-Font-Replacement](#zh-font-replacement)
  - [背景](#背景)
  - [项目简介](#项目简介)
  - [主要功能](#主要功能)
  - [重要须知](#重要须知)
  - [项目结构](#项目结构)
  - [流程总览](#流程总览)
  - [环境要求](#环境要求)
  - [依赖安装](#依赖安装)
  - [配置说明](#配置说明)
  - [字体包说明](#字体包说明)
  - [一键生成流程](#一键生成流程)
  - [设置额外字重生效（Windows）](#设置额外字重生效windows)
  - [更新日志](#更新日志)
  - [注意事项](#注意事项)
  - [License](#license)
  - [免责声明](#免责声明)
  - [致谢](#致谢)
  - [Full Name表](#full-name表)


---

## 项目结构

```
├── main.py               # 主流程入口
├── msyh_workflow.py      # 微软雅黑生成主流程
├── segoe_workflow.py     # Segoe UI 生成主流程
├── msyh_generate.py      # 微软雅黑生成核心脚本
├── segoe_generate.py     # Segoe UI 生成核心脚本
├── fetch_sarasa.py       # Sarasa Gothic 包版本获取、下载与解压
├── fetch_inter.py        # Inter 包版本获取、下载与解压
├── config.yaml           # 主配置文件
├── defualt_custom.template # 自定义字体包映射规则模板
├── utils/               # 工具函数集
│   ├── __init__.py      # 模块导出
│   ├── config.py        # 配置管理
│   ├── file_ops.py      # 文件操作
│   ├── archive.py       # 压缩/解压缩
│   ├── font_converter.py # 字体转换
│   ├── result_manager.py # 结果管理
│   ├── cleanup.py       # 清理功能
│   └── progress.py      # 进度显示
├── font_info/           # 字体 name 字段映射与元数据
├── result/              # 生成结果输出目录
├── source_files/        # 字体源包目录
└── temp/               # 临时文件目录
```

---

## 流程总览

```mermaid
graph TD
    A[开始] --> B[读取config.yaml]
    B --> C[开始流程]

    C --> D{是否启用 ENABLE_MS_YAHEI?}
    D -- 是 --> E[处理微软雅黑流程]

    C --> F{是否启用 ENABLE_SEGOE_UI?}
    F -- 是 --> G[处理Segoe UI流程]

    subgraph 微软雅黑处理
        E --> K{字体包获取模式}
        
        %% Custom模式分支
        K -- custom --> M2[使用自定义字体包]
        M2 --> O2[解压字体包]
        O2 --> P3[准备TTF文件]
        P3 --> Q2[按自定义映射规则修改字体信息]
        Q2 --> R2[生成TTC文件]
        R2 --> S[复制到结果目录]

        %% 标准模式分支
        K -- standard --> H{字体包来源}
        H -- online --> I[在线下载更纱黑体包]
        H -- local --> J[使用本地更纱黑体包]

        I --> I2[选择字体包类型]
        J --> I2
        I2 -- hinted --> O[解压字体包]
        I2 -- unhinted --> O

        O --> P0[准备TTF文件]
        P0 --> P4[重命名为msyhX.ttf]

        P4 --> S1{数字显示风格}
        S1 -- monospaced --> P1[使用等宽映射表]
        S1 -- proportional --> P2[使用不等宽映射表]
        
        P1 --> Q[修改字体信息]
        P2 --> Q
        Q --> R[生成TTC文件]
        R --> S
    end

    subgraph Segoe UI处理
        G --> T2{字体包获取模式}
        
        %% Custom模式分支
        T2 -- custom --> V2[使用自定义字体包]
        V2 --> X2[解压字体包]
        X2 --> Y3[寻找目标TTF文件]
        Y3 --> Z2[按自定义映射规则修改字体信息]
        Z2 --> AA2[生成TTF字体]
        AA2 --> AA[复制到结果目录]

        %% 标准模式分支
        T2 -- standard --> T3{字体包来源}
        T3 -- online --> U[在线下载Inter字体包]
        T3 -- local --> V[使用本地Inter字体包]

        U --> X[解压字体包]
        V --> X
        X --> Y0[准备TTF文件]

        Y0 --> S2{字符间距风格}
        S2 -- loose --> Y1[使用宽松映射表]
        S2 -- compact --> Y2[使用紧凑映射表]
        Y1 --> Z[修改字体信息]
        Y2 --> Z
        Z --> Z3[生成TTF字体]
        Z3 --> AA
    end

    S --> AB{是否清理临时文件?}
    AA --> AB
    AB -- 是 --> AC[清理temp目录]
    AB -- 否 --> AD[保留临时文件]

    AD --> AE[结束]
    AC --> AE

    %% 样式定义
    classDef decision fill:#f9f,stroke:#333,stroke-width:2px;
    classDef process fill:#bbf,stroke:#333,stroke-width:2px;
    class K,H,S1,T2,T3,S2,AB decision;
    class M2,I,J,O,Q,R,V2,U,V,Z process;
```

---

## 环境要求

- Python >= 3.11.13
- 推荐 Windows

## 依赖安装

```shell
pip install fonttools==4.58.4 py7zr==1.0.0 requests==2.32.4 pyyaml
```

---

## 配置说明

>[!IMPORTANT]
所有配置均由 [config.yaml](config.yaml) 控制。

## 字体包说明

- **更纱系列字体**（ SarasaGothicSC、SarasaUiSC）中英文字符外观一致。
  - 在阿拉伯数字上有区别：
    - **`Gothic` 标识**的是**不等宽设计**（Proportional），即每个字符宽度不同；
    - **`UI` 标识**的则是**等宽设计**，且数字 1 的底部多出一横。

- **Inter 字体**包含两种常见变体：`InterDisplay` 和 `Inter`。两者字符外观一致。
  - 区别在于，**带 `Display` 标识**的排版上会更加紧凑。

- **local 模式**：如使用 `FONT_PACKAGE_SOURCE: local` ，需将以下官方原版字体包放入 `source_files/` 目录，文件名保持原样：

  - Sarasa Gothic：
    - `SarasaGothicSC-TTF-<版本号>.7z` 或 `SarasaGothicSC-TTF-Unhinted-<版本号>.7z`
    - `SarasaUiSC-TTF-<版本号>.7z` 或 `SarasaUiSC-TTF-Unhinted-<版本号>.7z`
    - 推荐优先使用没有 `Unhinted` 标识的包，文件可从 [Sarasa Gothic Releases](https://github.com/be5invis/Sarasa-Gothic/releases) 获取
  - Inter：
    - `Inter-<版本号>.zip`，如 `Inter-4.1.zip`
    - 可从 [Inter Releases](https://github.com/rsms/inter/releases) 获取

> [!NOTE]  
  >
  >> 只需下载上述压缩包，无需手动解压。
  >>
  >> 文件名必须与官方 release 保持一致，否则自动识别会失败。

- **在线下载**：在yaml设置 `FONT_PACKAGE_SOURCE: online` 后，将自动下载最新字体包；若本地已有最新版本则跳过

- **自定义字体包**：通过 `FONT_PACKAGE_SOURCE: custom` 设置后，可以使用任意字体包，并指定[自定义映射规则](defualt_custom.template)。

---

## 一键生成流程

主流程入口：

```shell
python main.py
```

- 自动检测配置、准备目录
- 下载/解压 Sarasa Gothic、Inter 字体包
- 生成并伪装微软雅黑/Segoe UI 字体
- 结果输出至 `result/verXX-日期时间/`
- 可选自动清理临时文件


---

## 设置额外字重生效（Windows）

如需让极细和半粗字重在 Windows 下生效，请新建 reg 文件，内容如下：

>[!CAUTION]
>修改注册表前请备份
>
>操作不当可能导致系统问题

```reg
Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts]
"Microsoft YaHei Xlight & Microsoft YaHei UI Xlight"="msyhxl.ttc"
"Microsoft YaHei Semibold & Microsoft YaHei UI Semibold"="msyhsb.ttc"
```

保存后双击导入，重启生效。

与字体相关的注册表项，可参考[registry](registry.md)

---

## 更新日志

见[CHANGELOG](CHANGELOG.md)

---

## 注意事项

- 需 Python 3.11+，低版本不保证可用
- 字体包下载失败可手动放置至 `source_files/`
- 结果仅供本地开发、测试用途，勿用于商业分发
- 生成的 `version_report.txt` 会自动记录本次用到的 Sarasa/Inter 源包版本号，便于溯源和复现

---

## License

[CC BY-NC-SA 4.0](LICENSE)

---

## 免责声明
>[!CAUTION]
>
> 使用前请务必仔细阅读各项说明。
> 
> 使用本项目造成的任何后果，作者概不负责。
> 
> 本项目仅供学习、开发、测试用途，严禁用于任何商业用途或违法用途。
> 
> 所有生成字体均为伪装产物，非官方版本，与 Microsoft、Be5invis、Rasmus Andersson 等原作者无关。

---

## 致谢

- [Sarasa Gothic](https://github.com/be5invis/Sarasa-Gothic) 及其作者 Be5invis
- [Inter](https://github.com/rsms/inter) 及其作者 Rasmus Andersson
- [fontTools](https://github.com/fonttools/fonttools) 及相关开源社区
- [otf2ttf](https://github.com/awesometoolbox/otf2ttf) 及其作者 Hexazero
- 以及所有为字体自由与开源生态做出贡献的开发者

---

## Full Name表
>[!TIP]
>附上Full Name的CSV表参考
>
> (NameID=4, Lang=2052 or Lang=1032)

```csv
# msyh-Ver6.30
File,Index,Full Names
msyh.ttc,0,微软雅黑
msyh.ttc,1,Microsoft Yahei UI
msyhbd.ttc,0,微软雅黑 Bold
msyhbd.ttc,1,Microsoft Yahei UI Bold
msyhl.ttc,0,微软雅黑 Light
msyhl.ttc,1,Microsoft YaHei UI Light
```

```csv
# msyh-Ver11.3
File,Index,Full Names
msyh.ttc,0,Microsoft YaHei
msyh.ttc,1,Microsoft YaHei UI
msyhbd.ttc,0,Microsoft YaHei Bold
msyhbd.ttc,1,Microsoft YaHei UI Bold
msyhhv.ttc,0,Microsoft YaHei Heavy
msyhhv.ttc,1,Microsoft YaHei UI Heavy
msyhl.ttc,0,Microsoft YaHei Light
msyhl.ttc,1,Microsoft YaHei UI Light
msyhsb.ttc,0,Microsoft YaHei Semibold
msyhsb.ttc,1,Microsoft YaHei UI Semibold
msyhsl.ttc,0,Microsoft YaHei Semilight
msyhsl.ttc,1,Microsoft YaHei UI Semilight
```

```csv
# SegoeUI-Ver5.62
File,Index,Full Names
segoeui.ttf,0,Segoe UI
segoeuib.ttf,0,Segoe UI Bold
segoeuii.ttf,0,Segoe UI Italic
segoeuil.ttf,0,Segoe UI Light
segoeuisl.ttf,0,Segoe UI Semilight
segoeuiz.ttf,0,Segoe UI Bold Italic
seguibl.ttf,0,Segoe UI Black
seguibli.ttf,0,Segoe UI Black Italic
seguili.ttf,0,Segoe UI Light Italic
seguisb.ttf,0,Segoe UI Semibold
seguisbi.ttf,0,Segoe UI Semibold Italic
seguisli.ttf,0,Segoe UI Semilight Italic
```
