"""
更纱黑体字体包下载和解压模块
"""

import hashlib
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
API_URL = "https://api.github.com/repos/be5invis/Sarasa-Gothic/releases/latest"

# 全局缓存
_sarasa_version_cache = None


def get_version_and_assets():
    """在线获取 Sarasa 最新版本和 assets 信息
    :return: (version, assets) 元组
    """
    global _sarasa_version_cache
    if _sarasa_version_cache is not None:
        return _sarasa_version_cache
    try:
        response = req.get(
            API_URL, timeout=get_config_value(config, "DOWNLOAD_TIMEOUT", 10)
        )
        details = response.json()
        version = details["tag_name"][1:]
        assets = details.get("assets", [])
        logging.info(f"获取 Sarasa 在线版本信息成功: {version}")
        _sarasa_version_cache = (version, assets)
        return version, assets
    except Exception as e:
        logging.error(f"获取 Sarasa 在线版本信息失败: {e}")
        _sarasa_version_cache = (None, [])
        return None, []


def get_candidates(version):
    """根据配置获取需要下载的字体包列表
    :param version: 字体版本号
    :return: 候选文件名列表
    """
    sarasa_version = get_config_value(config, "SARASA_VERSION_STYLE", "normal")
    numerals_style = get_config_value(
        config, "MS_YAHEI_NUMERALS_STYLE", "monospaced"
    ).lower()
    candidates = []

    if numerals_style == "proportional":
        if sarasa_version == "hinted":
            candidates = [f"SarasaGothicSC-TTF-{version}.7z"]
        elif sarasa_version == "unhinted":
            candidates = [f"SarasaGothicSC-TTF-Unhinted-{version}.7z"]
    else:
        if sarasa_version == "hinted":
            candidates = [
                f"SarasaUiSC-TTF-{version}.7z",
                f"SarasaGothicSC-TTF-{version}.7z",
            ]
        elif sarasa_version == "unhinted":
            candidates = [
                f"SarasaUiSC-TTF-Unhinted-{version}.7z",
                f"SarasaGothicSC-TTF-Unhinted-{version}.7z",
            ]
    return candidates


def verify_file_hash(file_path, expected_hash):
    """验证文件的 SHA-256 哈希值
    :param file_path: 文件路径
    :param expected_hash: 预期的哈希值
    :return: 是否验证通过
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    actual_hash = sha256_hash.hexdigest()
    return expected_hash.lower() == actual_hash.lower()


def find_all_local_packages():
    """查找并用在线 assets 校验，校验失败自动重新下载
    :return: 有效的本地文件路径列表
    """
    dir_ = os.path.normpath(
        get_config_value(config, "SOURCE_FILES_DIR", "./source_files")
    )
    if not os.path.exists(dir_):
        return []

    files = os.listdir(dir_)
    version, assets = get_version_and_assets()
    candidates = get_candidates(version) if version else []

    if not candidates:
        for file in files:
            if file.startswith("SarasaUiSC-TTF-") or file.startswith(
                "SarasaMonoSC-TTF-"
            ):
                candidates.append(file)

    valid_files = []
    for file in files:
        if file not in candidates:
            continue

        target_path = os.path.normpath(os.path.join(dir_, file))
        asset = next((a for a in assets if a["name"] == file and "digest" in a), None)

        if asset:
            expected_hash = asset["digest"].replace("sha256:", "")
            if verify_file_hash(target_path, expected_hash):
                logging.info(f"本地文件 SHA-256 校验成功: {file}")
                valid_files.append(target_path)
            else:
                logging.error(f"本地文件 SHA-256 校验失败: {file}，将自动重新下载")
                # 自动重新下载
                url = next(
                    (a["browser_download_url"] for a in assets if a["name"] == file),
                    None,
                )
                if url:
                    try:
                        downloaded = download(url, dir_)
                        valid_files.append(downloaded)
                    except Exception as e:
                        logging.error(f"自动重新下载失败: {file}，原因: {e}")
        else:
            logging.warning(f"未找到在线校验信息: {file}，跳过 SHA-256 校验")
            valid_files.append(target_path)

    return valid_files


def get_all_latest():
    """获取所有最新字体包的下载链接
    :return: 下载链接列表
    """
    version, assets = get_version_and_assets()
    candidates = get_candidates(version)
    return [
        asset["browser_download_url"] for asset in assets if asset["name"] in candidates
    ]


def download(url, save_dir):
    """下载文件并显示进度条，下载后进行 SHA-256 校验
    :param url: 下载链接
    :param save_dir: 保存目录
    :return: 下载文件的路径
    """
    save_dir = os.path.normpath(save_dir)
    ensure_dir_exists(save_dir)

    filename = url.split("/")[-1]
    target_path = os.path.normpath(os.path.join(save_dir, filename))

    # 检查本地文件并校验
    if os.path.exists(target_path):
        version, assets = get_version_and_assets()
        asset = next(
            (a for a in assets if a["name"] == filename and "digest" in a), None
        )
        if asset:
            expected_hash = asset["digest"].replace("sha256:", "")
            if verify_file_hash(target_path, expected_hash):
                logging.info(f"本地文件 SHA-256 校验成功: {filename}")
                return target_path
            else:
                logging.error(f"本地文件 SHA-256 校验失败，将重新下载: {filename}")

    try:
        logging.info(f"开始下载: {filename}")
        resp = req.get(url, stream=True)
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

        # SHA-256校验
        version, assets = get_version_and_assets()
        asset = next(
            (a for a in assets if a["name"] == filename and "digest" in a), None
        )
        if asset:
            expected_hash = asset["digest"].replace("sha256:", "")
            if not verify_file_hash(target_path, expected_hash):
                os.remove(target_path)
                raise RuntimeError(f"SHA-256 校验失败: {filename}")
            logging.info(f"SHA-256 校验成功: {filename}")

        return target_path
    except Exception as e:
        logging.error(f"下载失败: {filename}, 错误: {e}")
        if os.path.exists(target_path):
            os.remove(target_path)
        raise RuntimeError(f"下载文件失败: {filename}") from e


def unzip(path):
    """解压字体包
    :param path: 字体包路径
    """
    out_dir = get_config_value(config, "TEMP_DIR", "./temp")
    out_dir = os.path.normpath(out_dir)
    logging.info(f"开始解压 {os.path.basename(path)} 到 {out_dir}")
    try:
        extract_archive(path, out_dir)
        logging.info("解压完成")
    except Exception as e:
        logging.error(f"解压失败: {e}")
        raise RuntimeError(f"解压文件失败: {os.path.basename(path)}") from e


if __name__ == "__main__":
    local_packages = find_all_local_packages()
    if local_packages:
        for package in local_packages:
            unzip(package)
    else:
        urls = get_all_latest()
        if not urls:
            raise RuntimeError("未找到更纱黑体最新包的下载链接")
        for url in urls:
            path = download(
                url, get_config_value(config, "SOURCE_FILES_DIR", "./source_files")
            )
            unzip(path)
