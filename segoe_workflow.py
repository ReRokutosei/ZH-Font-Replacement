import logging

import fetch_inter as inter
import segoe_generate
from utils.archive import extract_custom_font_packages
from utils.cleanup import clean_temp_dir
from utils.config import get_config_value
from utils.file_ops import create_directories


def generate_segoe_ui(config, result_subdir):
    logging.info("开始处理Inter->Segoe UI流程")

    # 确保目录存在
    create_directories(config)

    # custom 模式下直接用 config.yaml 指定的自定义英文字体包
    if get_config_value(config, "FONT_PACKAGE_SOURCE", "local") == "custom":
        # 若 temp 目录下未解压则主动解压一次
        try:
            extract_custom_font_packages(config)
            logging.info("自定义字体包解压完成")
        except Exception as e:
            logging.error(f"自定义字体包解压失败: {e}")
            raise
    else:
        # 下载并解压Inter
        try:
            inter.fetch_inter()
            logging.info("Inter字体包下载并解压完成")
        except Exception as e:
            logging.error(f"Inter字体包获取失败: {e}")
            raise

    # 调用segoe_generate模块处理字体生成
    try:
        segoe_generate.batch_rename_and_patch()
    except Exception as e:
        logging.error(f"Segoe UI字体生成失败: {e}")
        raise

    # 复制结果文件
    try:
        segoe_generate.copy_result_files(result_subdir)
    except Exception as e:
        logging.error(f"Segoe UI字体复制失败: {e}")
        raise

    # 清理临时文件（如果配置了的话）
    if get_config_value(config, "CLEAN_TEMP_ON_SUCCESS", False):
        clean_temp_dir(config)

    logging.info("Segoe UI字体处理完成")
