import shutil
import auto_configs as conf
import os


def copy_result(result_dir):
    # 主要输出文件
    main_files = [
        'msyh.ttc', 'msyhbd.ttc', 'msyhl.ttc', 'msyhel.ttc', 'msyhsb.ttc',
        'simsun.ttc', 'simsunb.ttf'
    ]
    for file in main_files:
        src = os.path.join(conf.TEMP_DIR, file)
        if os.path.exists(src):
            shutil.copy(src, result_dir)
    # 其他自定义文件
    for file in conf.OTHER_COPY:
        src = os.path.join(conf.TEMP_DIR, file)
        if os.path.exists(src):
            shutil.copy(src, result_dir)
