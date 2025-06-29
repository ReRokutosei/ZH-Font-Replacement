import config_utils
import fetch_original as fetch
import copy_result as copy
import logging
import sys
import os
import subprocess
import datetime

config = config_utils.load_config()

# FFPYTHON_PATH 由 config.yaml 配置
FFPYTHON_PATH = config['FFPYTHON_PATH']

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def validate_config():
    """验证配置的有效性"""
    if not any([
        config.get('ENABLE_MS_YAHEI', True),
        config.get('ENABLE_SIMSUN', True),
        config.get('ENABLE_SIMSUN_EXT', True),
        config.get('ENABLE_HANSCODE', True)
    ]):
        logging.error("错误：至少需要启用一项生成功能")
        sys.exit(1)

def create_directories():
    """创建必要的目录"""
    for d in [config.get('TEMP_DIR', './temp'), config.get('RESULT_DIR', './result'), config.get('SOURCE_FILES_DIR', './source_files')]:
        if not os.path.exists(d):
            os.makedirs(d)

def get_new_result_dir():
    # 生成 result/ver{num}-{datetime} 子目录
    now = datetime.datetime.now().strftime('%Y%m%d%H%M')
    base = config.get('RESULT_DIR', './result')
    # 查找已有 verXX- 前缀
    exist = [x for x in os.listdir(base) if x.startswith('ver') and os.path.isdir(os.path.join(base, x))]
    nums = [int(x[3:5]) for x in exist if x[3:5].isdigit()]
    num = max(nums) + 1 if nums else 1
    subdir = f'ver{num:02d}-{now}'
    full = os.path.join(base, subdir)
    os.makedirs(full, exist_ok=True)
    return full

def run_with_ffpython(script, func):
    result = subprocess.run([FFPYTHON_PATH, script, func])
    if result.returncode != 0:
        raise RuntimeError(f"{script} {func} 执行失败")

if __name__ == '__main__':
    try:
        logging.info("开始字体生成流程")
        validate_config()
        create_directories()
        # 获取所有源文件包
        if config.get('DOWNLOAD_MODE', 'local') == 'local':
            packages = fetch.find_all_local_packages()
            if not packages:
                logging.error("未找到任何本地源文件包，请检查 source_files 目录")
                sys.exit(1)
            for pkg in packages:
                logging.info(f"本地包: {pkg}")
                fetch.unzip(pkg)
        else:
            urls = fetch.get_all_latest()
            if not urls:
                logging.error("未找到任何可用的在线源文件包")
                sys.exit(1)
            for url in urls:
                logging.info(f"下载包: {url}")
                # 下载到 source_files 目录
                path = fetch.download(url, save_dir=config.get('SOURCE_FILES_DIR', './source_files'))
                fetch.unzip(path)
        # 生成唯一结果子目录
        result_subdir = get_new_result_dir()
        # 生成微软雅黑字体
        if config.get('ENABLE_MS_YAHEI', True):
            logging.info("开始生成微软雅黑字体")
            run_with_ffpython("generate_fonts.py", "gen_regular")
            run_with_ffpython("generate_fonts.py", "gen_bold")
            run_with_ffpython("generate_fonts.py", "gen_light")
            run_with_ffpython("generate_fonts.py", "gen_extralight")
            run_with_ffpython("generate_fonts.py", "gen_semibold")
            logging.info("微软雅黑字体生成完成")
        # 生成宋体
        if config.get('ENABLE_SIMSUN', True):
            logging.info("开始生成宋体")
            run_with_ffpython("generate_simsun.py", "gen_simsun_ttc")
            logging.info("宋体生成完成")
        # 生成宋体扩展
        if config.get('ENABLE_SIMSUN_EXT', True):
            logging.info("开始生成宋体扩展")
            run_with_ffpython("generate_simsun.py", "gen_simsun_ext")
            logging.info("宋体扩展生成完成")
        # 复制结果到唯一子目录
        copy.copy_result(result_subdir)
        logging.info(f"所有字体生成完成，结果目录：{result_subdir}")
    except Exception as e:
        logging.error(f"程序执行出错: {str(e)}")
        sys.exit(1)
