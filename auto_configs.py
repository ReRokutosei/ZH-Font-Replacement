import yaml
import os

# 读取配置
with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), encoding='utf-8') as f:
    _cfg = yaml.safe_load(f)

HINTED = _cfg.get('HINTED', True)
DOWNLOAD_MODE = _cfg.get('DOWNLOAD_MODE', 'local')
DOWNLOAD_TIMEOUT = _cfg.get('DOWNLOAD_TIMEOUT', 60)
SOURCE_FILES_DIR = _cfg.get('SOURCE_FILES_DIR', './source_files')

ENABLE_MS_YAHEI = _cfg.get('ENABLE_MS_YAHEI', True)
ENABLE_SIMSUN = _cfg.get('ENABLE_SIMSUN', True)
ENABLE_SIMSUN_EXT = _cfg.get('ENABLE_SIMSUN_EXT', True)
ENABLE_HANSCODE = _cfg.get('ENABLE_HANSCODE', True)

REGULAR_SOURCE = _cfg.get('REGULAR_SOURCE', 'SarasaUiSC-Regular')
BOLD_SOURCE = _cfg.get('BOLD_SOURCE', 'SarasaUiSC-Bold')
LIGHT_SOURCE = _cfg.get('LIGHT_SOURCE', 'SarasaUiSC-Light')
EXTRALIGHT_SOURCE = _cfg.get('EXTRALIGHT_SOURCE', 'SarasaUiSC-ExtraLight')
SEMIBOLD_SOURCE = _cfg.get('SEMIBOLD_SOURCE', 'SarasaUiSC-SemiBold')
SIMSUN_SOURCE = _cfg.get('SIMSUN_SOURCE', 'SarasaUiSC-Regular')

COPYRIGHT = _cfg.get('COPYRIGHT', 'Made from sarasa by chenh')
TEMP_DIR = _cfg.get('TEMP_DIR', './temp')
RESULT_DIR = _cfg.get('RESULT_DIR', './result')

OTHER_COPY = tuple(_cfg.get('OTHER_COPY', []))
