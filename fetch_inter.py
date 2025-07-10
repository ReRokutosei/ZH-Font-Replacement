"""
Inter 字体包下载和解压模块
"""

import logging
import os

import requests as req

from utils.archive import extract_archive
from utils.config import get_config_value, load_config
from utils.file_ops import ensure_dir_exists
from utils.progress import print_progress_bar

# 加载配置
config = load_config()

# GitHub API 地址
INTER_API_URL = "https://api.github.com/repos/rsms/inter/releases/latest"

# 全局缓存
_inter_version_cache = None


def get_inter_version_and_assets(silent=False):
    """在线获取 Inter 最新版本信息
    :param silent: 为 True 时不输出 info 日志
    :return: (version, assets) 元组
    """
    global _inter_version_cache
    if _inter_version_cache is not None:
        return _inter_version_cache
    try:
        response = req.get(
            INTER_API_URL, timeout=get_config_value(config, "DOWNLOAD_TIMEOUT", 10)
        )
        details = response.json()
        version = details.get("tag_name")
        assets = details.get("assets", [])
        if not silent:
            logging.info(f"获取 Inter 在线版本信息成功: {version}")
        _inter_version_cache = (version, assets)
        return version, assets
    except Exception as e:
        logging.error(f"获取 Inter 在线版本信息失败: {e}")
        _inter_version_cache = (None, [])
        return None, []


def find_local_inter_zip():
    """查找本地的 Inter 字体包
    :return: 找到的字体包路径，未找到则返回 None
    """
    dir_ = os.path.normpath(
        get_config_value(config, "SOURCE_FILES_DIR", "./source_files")
    )
    if not os.path.exists(dir_):
        return None
    files = os.listdir(dir_)
    zips = [f for f in files if f.startswith("Inter-") and f.endswith(".zip")]
    if not zips:
        return None
    zips.sort(reverse=True)
    return os.path.normpath(os.path.join(dir_, zips[0]))


def get_latest_inter_zip_url():
    """获取最新的 Inter 字体包下载链接
    :return: 下载链接，获取失败则返回 None
    """
    try:
        version, assets = get_inter_version_and_assets()
        for asset in assets:
            name = asset.get("name", "")
            if name.startswith("Inter-") and name.endswith(".zip"):
                return asset.get("browser_download_url")
    except Exception as e:
        logging.error(f"获取 Inter Releases 失败: {e}")
    return None


def download(url, save_dir=None):
    """下载文件并显示进度条
    :param url: 下载链接
    :param save_dir: 保存目录，默认为配置中的 SOURCE_FILES_DIR
    :return: 下载文件的路径
    """
    if save_dir is None:
        save_dir = get_config_value(config, "SOURCE_FILES_DIR", "./source_files")
    save_dir = os.path.normpath(save_dir)
    ensure_dir_exists(save_dir)

    filename = url.split("/")[-1]
    target_path = os.path.normpath(os.path.join(save_dir, filename))
    if os.path.exists(target_path):
        logging.info(f"文件已存在，跳过下载: {filename}")
        return target_path

    try:
        resp = req.get(
            url, timeout=get_config_value(config, "DOWNLOAD_TIMEOUT", 10), stream=True
        )
        total_size = int(resp.headers.get("content-length", 0))
        downloaded_size = 0

        with open(target_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    print_progress_bar(
                        downloaded_size,
                        total_size,
                        prefix="下载进度",
                        suffix=f"{downloaded_size}/{total_size} 字节",
                        length=30,
                    )

        print()  # 进度条完成后换行
        logging.info(f"下载完成: {filename}")
        return target_path
    except Exception as e:
        logging.error(f"下载失败: {filename}, 错误: {e}")
        if os.path.exists(target_path):
            os.remove(target_path)
        raise RuntimeError(f"下载文件失败: {filename}") from e


def unzip_inter(path, out_dir=None):
    """解压 Inter 字体包
    :param path: 字体包路径
    :param out_dir: 解压目录，默认为配置中的 TEMP_DIR
    """
    if out_dir is None:
        out_dir = get_config_value(config, "TEMP_DIR", "./temp")
    out_dir = os.path.normpath(out_dir)
    logging.info(f"开始解压 {os.path.basename(path)} 到 {out_dir}")
    try:
        extract_archive(path, out_dir)
        logging.info("解压完成")
    except Exception as e:
        logging.error(f"解压失败: {e}")
        raise RuntimeError(f"解压文件失败: {os.path.basename(path)}") from e


def fetch_inter():
    """获取 Inter 字体包（优先使用本地包）
    :return: 字体包路径
    """
    local_zip = find_local_inter_zip()
    if local_zip:
        logging.info(f"已存在本地 Inter 包，跳过下载: {os.path.basename(local_zip)}")
        unzip_inter(local_zip)
        return local_zip

    url = get_latest_inter_zip_url()
    if not url:
        raise RuntimeError("未找到 Inter 最新 zip 包的下载链接")

    logging.info(f"下载 Inter 包: {url}")
    zip_path = download(url)
    unzip_inter(zip_path)
    return zip_path


if __name__ == "__main__":
    fetch_inter()
