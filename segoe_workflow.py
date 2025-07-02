import json
import logging
import os
import shutil

import segoe_generate


def generate_segoe_ui(config, result_subdir):
    logging.info("开始处理Inter->Segoe UI流程")
    import fetch_inter as inter
    inter.fetch_inter()  # 下载并解压Inter
    extras_ttf_dir = os.path.join(config.get('TEMP_DIR', './temp'), 'extras', 'ttf')
    mapping = segoe_generate.get_segoe_mapping()
    for segoe_name, inter_name in mapping:
        src = os.path.join(extras_ttf_dir, inter_name)
        dst = os.path.join(segoe_generate.DST_DIR, segoe_name)
        if os.path.exists(src):
            shutil.copy(src, dst)
        else:
            logging.warning(f"未找到 Inter ttf: {src}")
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
        if os.path.exists(src):
            shutil.copy(src, result_subdir)
    logging.info("Segoe UI字体处理完成")
