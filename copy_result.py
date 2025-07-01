import shutil
import yaml
import os

config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
with open(config_path, encoding='utf-8') as f:
    config = yaml.safe_load(f)


def copy_result(result_dir):
    main_files = [
        'msyh.ttc', 'msyhbd.ttc', 'msyhl.ttc', 'msyhxl.ttc', 'msyhsb.ttc'
    ]
    for file in main_files:
        src = os.path.join(config.get('TEMP_DIR', './temp'), file)
        if os.path.exists(src):
            shutil.copy(src, result_dir)
