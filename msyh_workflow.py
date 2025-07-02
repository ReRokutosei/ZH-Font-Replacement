import logging
import os
import subprocess
import sys

import copy_result as copy


def run_with_python(script, *args):
    result = subprocess.run([sys.executable, script] + list(args))
    if result.returncode != 0:
        raise RuntimeError(f"{script} {' '.join(args)} 执行失败")

def check_ttc_generated(config):
    temp_dir = config.get('TEMP_DIR', './temp')
    ttc_files = ["msyh.ttc", "msyhbd.ttc", "msyhl.ttc", "msyhxl.ttc", "msyhsb.ttc"]
    return all(os.path.exists(os.path.join(temp_dir, f)) for f in ttc_files)

def generate_ms_yahei(config, result_subdir):
    logging.info("开始生成微软雅黑字体")
    run_with_python("msyh_generate.py", "gen_regular")
    run_with_python("msyh_generate.py", "gen_bold")
    run_with_python("msyh_generate.py", "gen_light")
    run_with_python("msyh_generate.py", "gen_extralight")
    run_with_python("msyh_generate.py", "gen_semibold")
    if check_ttc_generated(config):
        copy.copy_result(result_subdir)
        logging.info("微软雅黑字体生成完成，并已复制到结果目录")
    else:
        logging.error("微软雅黑字体未生成任何文件，请检查流程！")
        sys.exit(1)
