# 源文件下载配置
HINTED = True  # 是否下载 Hinted 版本
DOWNLOAD_MODE = 'local'  # 下载模式：'auto'-优先网络下载，失败时使用本地文件；'local'-仅使用本地文件
DOWNLOAD_TIMEOUT = 60  # 下载超时时间（秒）
SOURCE_FILES_DIR = './source_files'  # 本地源文件目录

# 功能开关（至少启用其中一项，否则程序将报错）
ENABLE_MS_YAHEI = True      # 是否生成微软雅黑字体
ENABLE_SIMSUN = True        # 是否生成宋体
ENABLE_SIMSUN_EXT = True    # 是否生成宋体扩展
ENABLE_HANSCODE = True      # 是否生成等宽编程字体

# 字体文件配置
REGULAR_SOURCE = 'SarasaUiSC-Regular'    # 标准字体来源的文件名
BOLD_SOURCE = 'SarasaUiSC-Bold'          # 粗体来源的文件名
LIGHT_SOURCE = 'SarasaUiSC-Light'        # 细体来源的文件名
EXTRALIGHT_SOURCE = 'SarasaUiSC-ExtraLight'  # 极细体来源的文件名
SEMIBOLD_SOURCE = 'SarasaUiSC-SemiBold'  # 半粗体来源的文件名
SIMSUN_SOURCE = 'SarasaUiSC-Regular'      # 宋体来源的文件名

# 基础配置
COPYRIGHT = 'Made from sarasa by chenh'  # 字体的 Copyright
TEMP_DIR = './temp'      # 临时目录
RESULT_DIR = './result'  # 结果目录

OTHER_COPY = ()  # 你想复制的其他文件到结果目录
