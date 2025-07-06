"""
清理模块
负责临时文件和目录的清理操作
"""

import logging
import os
import shutil


def clean_temp_dir(config):
    """清理临时目录"""
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