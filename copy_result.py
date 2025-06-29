import shutil
import config_utils
import os

config = config_utils.load_config()


def copy_result(result_dir):
    # 主要输出文件
    main_files = [
        'msyh.ttc', 'msyhbd.ttc', 'msyhl.ttc', 'msyhel.ttc', 'msyhsb.ttc',
        'simsun.ttc', 'simsunb.ttf'
    ]
    for file in main_files:
        src = os.path.join(config.get('TEMP_DIR', './temp'), file)
        if os.path.exists(src):
            shutil.copy(src, result_dir)
    # 其他自定义文件
    for file in (config.get('OTHER_COPY') or []):
        src = os.path.join(config.get('TEMP_DIR', './temp'), file)
        if os.path.exists(src):
            shutil.copy(src, result_dir)
    # 复制 HansCode 编程字体
    for file in os.listdir(config.get('TEMP_DIR', './temp')):
        if file.startswith('HansCode-') and file.endswith('.ttf'):
            src = os.path.join(config.get('TEMP_DIR', './temp'), file)
            shutil.copy(src, result_dir)
