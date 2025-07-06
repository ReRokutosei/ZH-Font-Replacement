import logging

import fetch_inter as inter
import segoe_generate
from utils.config import get_config_value
from utils.archive import extract_custom_font_packages


def generate_segoe_ui(config, result_subdir):
    logging.info("开始处理Inter->Segoe UI流程")
    
    # custom 模式下直接用 config.yaml 指定的自定义英文字体包
    if get_config_value(config, 'FONT_PACKAGE_SOURCE', 'local') == 'custom':
        # 若 temp 目录下未解压则主动解压一次
        extract_custom_font_packages(config)
    else:
        inter.fetch_inter()  # 下载并解压Inter
    
    # 调用segoe_generate模块处理字体生成
    segoe_generate.batch_rename_and_patch()
    
    # 复制结果文件
    segoe_generate.copy_result_files(result_subdir)
    
    logging.info("Segoe UI字体处理完成")
