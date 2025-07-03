import json
import logging
import os
import shutil

import fetch_inter as inter
import project_utils
import segoe_generate
from project_utils import extract_custom_font_packages, safe_copy


def generate_segoe_ui(config, result_subdir):
    logging.info("开始处理Inter->Segoe UI流程")
    temp_dir = config.get('TEMP_DIR', './temp')
    mapping = segoe_generate.get_segoe_mapping()
    # custom 模式下直接用 config.yaml 指定的自定义英文字体包
    if config.get('FONT_PACKAGE_SOURCE', 'local') == 'custom':
        # 若 temp 目录下未解压则主动解压一次
        extract_custom_font_packages(config)
    else:
        inter.fetch_inter()  # 下载并解压Inter
    for segoe_name, inter_name in mapping:
        try:
            rel_src_path = project_utils.find_font_file(temp_dir, inter_name)
            src = os.path.join(temp_dir, rel_src_path)
            dst = os.path.join(segoe_generate.DST_DIR, segoe_name)
            safe_copy(src, dst)
        except Exception as e:
            logging.warning(f"未找到 Inter ttf: {inter_name}，查找异常: {e}")
    with open('./font_info/segoe_font_info.json', 'r', encoding='utf-8') as f:
        infos = json.load(f)
    info_map = {info['file'].lower(): info for info in infos}
    for segoe_name, inter_name in mapping:
        segoe_out = os.path.join(segoe_generate.DST_DIR, segoe_name)
        info = info_map.get(segoe_name.lower())
        if info and os.path.exists(segoe_out):
            segoe_generate.copy_font_info(segoe_out, info)
    for segoe_name, _ in mapping:
        src = os.path.join(segoe_generate.DST_DIR, segoe_name)
        try:
            safe_copy(src, result_subdir)
        except Exception:
            pass
    logging.info("Segoe UI字体处理完成")
