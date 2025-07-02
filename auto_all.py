import datetime
import json
import logging
import os
import shutil
import subprocess
import sys

import yaml
from fontTools.ttLib import TTCollection

import copy_result as copy
import fetch_inter as inter
import fetch_sarasa as sarasa
import segoe_generate

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# config = config_utils.load_config()
config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
with open(config_path, encoding='utf-8') as f:
    config = yaml.safe_load(f)

def validate_config():
    """验证配置的有效性"""
    if not config.get('ENABLE_MS_YAHEI', True) and not config.get('ENABLE_SEGOE_UI', True):
        logging.error("错误：至少需要启用一项生成功能（微软雅黑/Segoe UI）")
        sys.exit(1)

def create_directories():
    """创建必要的目录"""
    for d in [config.get('TEMP_DIR', './temp'), config.get('RESULT_DIR', './result'), config.get('SOURCE_FILES_DIR', './source_files')]:
        d = os.path.normpath(d)
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

def run_with_python(script, *args):
    result = subprocess.run([sys.executable, script] + list(args))
    if result.returncode != 0:
        raise RuntimeError(f"{script} {' '.join(args)} 执行失败")

# def split_ttc_to_ttf(ttc_path, out_dir, ttf_names):
#     """将 ttc 拆分为多个 ttf 文件"""
#     if not os.path.exists(ttc_path):
#         raise FileNotFoundError(f"未找到 Inter.ttc: {ttc_path}")
#     ttc = TTCollection(ttc_path)
#     if len(ttc.fonts) < len(ttf_names):
#         raise RuntimeError(f"TTC 包含字体数不足: {len(ttc.fonts)} < {len(ttf_names)}")
#     for i, name in enumerate(ttf_names):
#         out_path = os.path.join(out_dir, name)
#         ttc.fonts[i].save(out_path)

if __name__ == '__main__':
    try:
        logging.info("开始字体生成流程")
        validate_config()
        create_directories()
        # 获取所有源文件包
        if config.get('ENABLE_MS_YAHEI', True):
            if config.get('DOWNLOAD_MODE', 'local') == 'local':
                packages = sarasa.find_all_local_packages()
                if not packages:
                    logging.error("未找到任何本地源文件包，请检查 source_files 目录")
                    sys.exit(1)
                for pkg in packages:
                    logging.info(f"本地包: {pkg}")
                    sarasa.unzip(pkg)
            else:
                urls = sarasa.get_all_latest()
                if not urls:
                    logging.error("未找到任何可用的在线源文件包")
                    sys.exit(1)
                for url in urls:
                    filename = os.path.basename(url)
                    local_path = os.path.normpath(os.path.join(config.get('SOURCE_FILES_DIR', './source_files'), filename))
                    if os.path.exists(local_path):
                        logging.info(f"已存在本地最新版本包，跳过下载: {filename}")
                        logging.info(f"准备解压: {filename}")
                        sarasa.unzip(local_path)
                    else:
                        logging.info(f"下载包: {url}")
                        path = sarasa.download(url, save_dir=config.get('SOURCE_FILES_DIR', './source_files'))
                        logging.info(f"准备解压: {os.path.basename(path)}")
                        sarasa.unzip(path)
        # 生成唯一结果子目录
        result_subdir = os.path.normpath(get_new_result_dir())
        # 生成微软雅黑字体
        if config.get('ENABLE_MS_YAHEI', True):
            logging.info("开始生成微软雅黑字体")
            run_with_python("msyh_generate.py", "gen_regular")
            run_with_python("msyh_generate.py", "gen_bold")
            run_with_python("msyh_generate.py", "gen_light")
            run_with_python("msyh_generate.py", "gen_extralight")
            run_with_python("msyh_generate.py", "gen_semibold")

            def check_ttc_generated():
                temp_dir = config.get('TEMP_DIR', './temp')
                ttc_files = ["msyh.ttc", "msyhbd.ttc", "msyhl.ttc", "msyhxl.ttc", "msyhsb.ttc"]
                return all(os.path.exists(os.path.join(temp_dir, f)) for f in ttc_files)
            if check_ttc_generated():
                copy.copy_result(result_subdir)
                logging.info("微软雅黑字体生成完成，并已复制到结果目录")
            else:
                logging.error("微软雅黑字体未生成任何文件，请检查流程！")
                sys.exit(1)
        # 生成Segoe UI字体
        if config.get('ENABLE_SEGOE_UI', True):
            logging.info("开始处理Inter->Segoe UI流程")
            inter.fetch_inter()  # 下载并解压Inter
            # 直接从 ./temp/extras/ttf/ 复制并重命名
            extras_ttf_dir = os.path.join(config.get('TEMP_DIR', './temp'), 'extras', 'ttf')
            mapping = segoe_generate.get_segoe_mapping()
            for segoe_name, inter_name in mapping:
                src = os.path.join(extras_ttf_dir, inter_name)
                dst = os.path.join(segoe_generate.DST_DIR, segoe_name)
                if os.path.exists(src):
                    shutil.copy(src, dst)
                else:
                    logging.warning(f"未找到 Inter ttf: {src}")
            # 读取 segoe_font_info.json，构建 info_map
            with open('./font_info/segoe_font_info.json', 'r', encoding='utf-8') as f:
                infos = json.load(f)
            info_map = {info['file'].lower(): info for info in infos}
            # 直接批量处理
            for segoe_name, inter_name in mapping:
                segoe_out = os.path.join(segoe_generate.DST_DIR, segoe_name)
                info = info_map.get(segoe_name.lower())
                if info and os.path.exists(segoe_out):
                    segoe_generate.copy_font_info(segoe_out, info)
            # 复制12个ttf到结果目录
            for segoe_name, _ in mapping:
                src = os.path.join(segoe_generate.DST_DIR, segoe_name)
                if os.path.exists(src):
                    shutil.copy(src, result_subdir)
            logging.info("Segoe UI字体处理完成")
        logging.info(f"所有字体生成完成，结果目录：{os.path.normpath(result_subdir)}")
        # 自动清理 temp 目录（可选）
        if config.get('CLEAN_TEMP_ON_SUCCESS', False):
            temp_dir = os.path.normpath(config.get('TEMP_DIR', './temp'))
            for filename in os.listdir(temp_dir):
                file_path = os.path.normpath(os.path.join(temp_dir, filename))
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    logging.warning(f"清理 temp 文件失败: {file_path}，原因: {e}")
            logging.info("已清理 temp 目录下所有文件。")
    except Exception as e:
        logging.error(f"程序执行出错: {str(e)}")
        sys.exit(1)
