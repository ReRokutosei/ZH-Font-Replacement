import logging
import os
import subprocess
import sys


from project_utils import (find_font_file, get_config_value, load_config,
                           safe_copy)

config = load_config()

def run_with_python(script, *args):
    result = subprocess.run([sys.executable, script] + list(args))
    if result.returncode != 0:
        raise RuntimeError(f"{script} {' '.join(args)} 执行失败")

def check_ttc_generated(config):
    temp_dir = config.get('TEMP_DIR', './temp')
    ttc_files = ["msyh.ttc", "msyhbd.ttc", "msyhl.ttc", "msyhxl.ttc", "msyhsb.ttc"]
    # 用 find_font_file 检查每个文件是否存在
    for f in ttc_files:
        try:
            find_font_file(temp_dir, f)
        except Exception:
            return False
    return True


def copy_result(result_dir):
    main_files = [
        'msyh.ttc', 'msyhbd.ttc', 'msyhl.ttc', 'msyhxl.ttc', 'msyhsb.ttc'
    ]


    for file in main_files:
        src = os.path.join(get_config_value(config, 'TEMP_DIR', './temp'), file)
        try:
            safe_copy(src, result_dir)
        except Exception:
            pass

def generate_ms_yahei(config, result_subdir):
    logging.info("开始生成微软雅黑字体")
    run_with_python("msyh_generate.py", "gen_regular")
    run_with_python("msyh_generate.py", "gen_bold")
    run_with_python("msyh_generate.py", "gen_light")
    run_with_python("msyh_generate.py", "gen_extralight")
    run_with_python("msyh_generate.py", "gen_semibold")
    if check_ttc_generated(config):
        copy_result(result_subdir)
        logging.info("微软雅黑字体生成完成，并已复制到结果目录")
    else:
        logging.error("微软雅黑字体未生成任何文件，请检查流程！")
        raise RuntimeError("微软雅黑字体未生成任何文件，请检查流程！")
