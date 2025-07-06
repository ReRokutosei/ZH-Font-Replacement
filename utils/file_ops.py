"""
文件操作模块
负责文件系统相关的操作，如目录创建、文件复制、查找等
"""

import logging
import os
import shutil


def ensure_dir_exists(path):
    """
    确保目录存在，不存在则创建。
    """
    path = os.path.normpath(path)
    if not os.path.exists(path):
        os.makedirs(path)


def create_directories(config):
    """创建项目所需的目录"""
    for d in [
        config.get("TEMP_DIR", "./temp"),
        config.get("RESULT_DIR", "./result"),
        config.get("SOURCE_FILES_DIR", "./source_files"),
    ]:
        ensure_dir_exists(d)


def safe_copy(src, dst, overwrite=True):
    """
    拷贝文件，自动判断存在性，默认覆盖。
    """
    if not os.path.isfile(src):
        raise FileNotFoundError(f"源文件不存在: {src}")
    if os.path.exists(dst):
        if not overwrite:
            return
        if os.path.isdir(dst):
            raise IsADirectoryError(f"目标是目录: {dst}")
    ensure_dir_exists(os.path.dirname(dst))
    shutil.copy2(src, dst)


def find_font_file(root_dir, target_name):
    """
    在 root_dir 下递归查找名为 target_name 的文件，返回相对路径（相对于 root_dir）。
    若未找到则抛出 FileNotFoundError。
    """
    # 防御性：只允许普通文件名，防止特殊字符
    if not isinstance(target_name, str) or any(
        c in target_name for c in r"/\\:*?\"<>|"
    ):
        raise ValueError(f"非法文件名: {target_name}")
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname == target_name:
                rel_path = os.path.relpath(os.path.join(dirpath, fname), root_dir)
                return rel_path
    raise FileNotFoundError(f"未在 {root_dir} 下找到目标文件: {target_name}")
