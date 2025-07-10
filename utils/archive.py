"""
压缩解压模块
负责zip和7z格式文件的解压操作
"""

import os
import zipfile

import py7zr as sz


def extract_archive(archive_path, out_dir):
    """
    自动判断 zip/7z 并解压到 out_dir。
    """
    ext = os.path.splitext(archive_path)[1].lower()
    from .file_ops import ensure_dir_exists

    ensure_dir_exists(out_dir)
    if ext == ".zip":
        with zipfile.ZipFile(archive_path, "r") as zf:
            zf.extractall(out_dir)
    elif ext == ".7z":
        with sz.SevenZipFile(archive_path, mode="r") as archive:
            archive.extractall(path=out_dir)
    else:
        raise RuntimeError(f"仅支持 zip/7z 格式，错误文件: {archive_path}")


def extract_custom_font_packages(config):
    """
    解压 config.yaml 中指定的 CUSTOM_MS_YAHEI_PACKAGE 和 CUSTOM_SEGOE_PACKAGE 到 TEMP_DIR。
    仅支持 zip/7z 格式。
    """
    source_dir = os.path.abspath(config.get("SOURCE_FILES_DIR", "./source_files"))
    temp_dir = os.path.abspath(config.get("TEMP_DIR", "./temp"))
    os.makedirs(temp_dir, exist_ok=True)

    def extract_font_package(pkg_item):
        pkg_path = (
            pkg_item if os.path.isabs(pkg_item) else os.path.join(source_dir, pkg_item)
        )
        pkg_path = os.path.abspath(pkg_path)
        if not os.path.isfile(pkg_path):
            raise RuntimeError(f"自定义字体包不存在: {pkg_path}")
        ext = os.path.splitext(pkg_path)[1].lower()
        if ext == ".zip":
            # 始终用zipfile并强制用gbk修正文件名，兼容所有中文zip
            with zipfile.ZipFile(pkg_path, "r") as zf:
                for info in zf.infolist():
                    name = info.filename
                    try:
                        name_gbk = name.encode("cp437").decode("gbk")
                    except Exception:
                        name_gbk = name
                    target_path = os.path.join(temp_dir, name_gbk)
                    if info.is_dir():
                        os.makedirs(target_path, exist_ok=True)
                    else:
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        with zf.open(info) as src, open(target_path, "wb") as dst:
                            dst.write(src.read())
        elif ext == ".7z":
            with sz.SevenZipFile(pkg_path, mode="r") as archive:
                archive.extractall(path=temp_dir)
        else:
            raise RuntimeError(f"仅支持 zip/7z 格式，自定义字体包错误: {pkg_path}")

    if config.get("ENABLE_MS_YAHEI", True):
        ms_pkg = config.get("CUSTOM_MS_YAHEI_PACKAGE", "")
        if not ms_pkg:
            raise RuntimeError("未指定自定义中文字体包路径 (config.yaml)")
        if isinstance(ms_pkg, list):
            for pkg in ms_pkg:
                extract_font_package(pkg)
        else:
            extract_font_package(ms_pkg)
    if config.get("ENABLE_SEGOE_UI", True):
        se_pkg = config.get("CUSTOM_SEGOE_PACKAGE", "")
        if not se_pkg:
            raise RuntimeError("未指定自定义英文字体包路径 (config.yaml)")
        if isinstance(se_pkg, list):
            for pkg in se_pkg:
                extract_font_package(pkg)
        else:
            extract_font_package(se_pkg)
