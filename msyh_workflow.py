import logging

from msyh_generate import (
    batch_copy_msyh_ttf,
    batch_generate_ttc,
    batch_patch_names,
    check_ttc_generated,
    copy_individual_ttf_to_result,
    copy_result_files,
)
from utils.cleanup import clean_temp_dir
from utils.config import get_config_value
from utils.file_ops import create_directories


def generate_ms_yahei(config, result_subdir):
    logging.info("开始生成微软雅黑字体")

    # 确保目录存在
    create_directories(config)

    try:
        # 复制源TTF文件
        batch_copy_msyh_ttf()
        logging.info("源TTF文件复制完成")
    except Exception as e:
        logging.error(f"源TTF文件复制失败: {e}")
        raise

    try:
        # 设置字体名称
        batch_patch_names()
        logging.info("字体名称设置完成")
    except Exception as e:
        logging.error(f"字体名称设置失败: {e}")
        raise

    try:
        # 生成TTC文件
        batch_generate_ttc()
        logging.info("TTC文件生成完成")
    except Exception as e:
        logging.error(f"TTC文件生成失败: {e}")
        raise

    if check_ttc_generated():
        try:
            # 复制TTC文件到结果目录
            copy_result_files(result_subdir)
            # 复制覆写元信息的TTF文件（如果配置启用）
            copy_individual_ttf_to_result(result_subdir)
            logging.info("微软雅黑字体生成完成，并已复制到结果目录")
        except Exception as e:
            logging.error(f"结果文件复制失败: {e}")
            raise
    else:
        error_msg = "微软雅黑字体未生成任何文件，请检查流程！"
        logging.error(error_msg)
        raise RuntimeError(error_msg)

    # 清理临时文件（如果配置了的话）
    if get_config_value(config, "CLEAN_TEMP_ON_SUCCESS", False):
        clean_temp_dir(config)
