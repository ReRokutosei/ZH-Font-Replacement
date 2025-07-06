import hashlib
import logging
import os
import time

import requests as req
import yaml

from utils.file_ops import ensure_dir_exists
from utils.archive import extract_archive
from utils.progress import print_progress_bar


config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
with open(config_path, encoding='utf-8') as f:
    config = yaml.safe_load(f)
if not isinstance(config, dict):
    raise RuntimeError(f"config.yaml 解析异常，返回类型: {type(config)}, 内容: {config}")

API_URL = 'https://api.github.com/repos/be5invis/Sarasa-Gothic/releases/latest'


# 全局缓存
_sarasa_version_cache = None

def get_version_and_assets():
    """在线获取 Sarasa 最新版本和 assets 信息"""
    global _sarasa_version_cache
    if _sarasa_version_cache is not None:
        return _sarasa_version_cache
    try:
        response = req.get(API_URL, timeout=config.get('DOWNLOAD_TIMEOUT', 10))
        details = response.json()
        version = details['tag_name'][1:]
        assets = details.get('assets', [])
        logging.info(f"获取 Sarasa 在线版本信息成功: {version}")
        _sarasa_version_cache = (version, assets)
        return version, assets
    except Exception as e:
        logging.error(f"获取 Sarasa 在线版本信息失败: {e}")
        _sarasa_version_cache = (None, [])
        return None, []

def get_candidates(version):
    sarasa_version = config.get('SARASA_VERSION_STYLE', 'normal')
    numerals_style = config.get('MS_YAHEI_NUMERALS_STYLE', 'monospaced').lower()
    candidates = []
    if numerals_style == 'proportional':
        if sarasa_version == 'hinted':
            candidates = [f'SarasaGothicSC-TTF-{version}.7z']
        elif sarasa_version == 'unhinted':
            candidates = [f'SarasaGothicSC-TTF-Unhinted-{version}.7z']
    else:
        if sarasa_version == 'hinted':
            candidates = [
                f'SarasaUiSC-TTF-{version}.7z',
                f'SarasaGothicSC-TTF-{version}.7z',
            ]
        elif sarasa_version == 'unhinted':
            candidates = [
                f'SarasaUiSC-TTF-Unhinted-{version}.7z',
                f'SarasaGothicSC-TTF-Unhinted-{version}.7z',
            ]
    return candidates

def find_all_local_packages():
    """查找并用在线 assets 校验，校验失败自动重新下载"""
    dir_ = os.path.normpath(config.get('SOURCE_FILES_DIR', './source_files'))
    if not os.path.exists(dir_):
        return []
    files = os.listdir(dir_)
    version, assets = get_version_and_assets()
    candidates = get_candidates(version) if version else []
    if not candidates:
        for file in files:
            if file.startswith('SarasaUiSC-TTF-') or file.startswith('SarasaMonoSC-TTF-'):
                candidates.append(file)

    valid_files = []
    for file in files:
        if file in candidates:
            asset_name = file
            asset = None
            for a in assets:
                if a['name'] == asset_name and 'digest' in a:
                    asset = a
                    break
            target_path = os.path.normpath(os.path.join(dir_, asset_name))
            if asset:
                expected_hash = asset['digest'].replace('sha256:', '')
                sha256_hash = hashlib.sha256()
                with open(target_path, 'rb') as f:
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(byte_block)
                actual_hash = sha256_hash.hexdigest()
                if expected_hash.lower() == actual_hash.lower():
                    logging.info(f"本地文件 SHA-256 校验成功: {asset_name}")
                    valid_files.append(target_path)
                else:
                    logging.error(f"本地文件 SHA-256 校验失败: {asset_name}，将自动重新下载")
                    # 自动重新下载
                    url = None
                    for a in assets:
                        if a['name'] == asset_name:
                            url = a['browser_download_url']
                            break
                    if url:
                        try:
                            downloaded = download(url, dir_)
                            valid_files.append(downloaded)
                        except Exception as e:
                            logging.error(f"自动重新下载失败: {asset_name}，原因: {e}")
            else:
                logging.warning(f"未找到在线校验信息: {asset_name}，跳过 SHA-256 校验")
                valid_files.append(target_path)
    return valid_files

def get_all_latest():
    version, assets = get_version_and_assets()
    candidates = get_candidates(version)
    urls = []
    for asset in assets:
        if asset['name'] in candidates:
            urls.append(asset['browser_download_url'])
    return urls

def download(url, save_dir):
    save_dir = os.path.normpath(save_dir)
    ensure_dir_exists(save_dir)
    filename = url.split('/')[-1]
    target_path = os.path.normpath(os.path.join(save_dir, filename))

    # 检查本地文件并校验
    if os.path.exists(target_path):
        asset_name = filename
        version, assets = get_version_and_assets()
        asset = None
        for a in assets:
            if a['name'] == asset_name and 'digest' in a:
                asset = a
                break
        if asset:
            expected_hash = asset['digest'].replace('sha256:', '')
            sha256_hash = hashlib.sha256()
            with open(target_path, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            actual_hash = sha256_hash.hexdigest()
            if expected_hash.lower() == actual_hash.lower():
                logging.info(f"本地文件 SHA-256 校验成功: {asset_name}")
                return target_path
            else:
                logging.error(f"本地文件 SHA-256 校验失败，将重新下载: {asset_name}")

    logging.info(f"开始下载: {filename}")
    resp = req.get(url, stream=True)
    total_size = int(resp.headers.get('content-length', 0))
    downloaded_size = 0
    start_time = time.time()

    with open(target_path, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded_size += len(chunk)
                print_progress_bar(downloaded_size, total_size, prefix='下载进度', suffix=f'{downloaded_size}/{total_size} 字节', length=30)
    logging.info(f"\n下载完成: {filename}")

    # SHA-256校验
    version, assets = get_version_and_assets()
    asset = None
    for a in assets:
        if a['name'] == filename and 'digest' in a:
            asset = a
            break
    if asset:
        expected_hash = asset['digest'].replace('sha256:', '')
        sha256_hash = hashlib.sha256()
        with open(target_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        actual_hash = sha256_hash.hexdigest()
        if expected_hash.lower() != actual_hash.lower():
            logging.error(f"SHA-256 校验失败: {filename} | 预期: {expected_hash} | 实际: {actual_hash}")
            raise ValueError(f"SHA-256校验失败: {filename} | 预期值: {expected_hash} | 实际值: {actual_hash}")
        logging.info(f"SHA-256 校验成功: {filename}")
    else:
        logging.warning(f"未找到在线校验信息: {filename}，跳过 SHA-256 校验")
    return target_path

def unzip(path):
    out_dir = os.path.normpath(config.get('TEMP_DIR', './temp'))
    logging.info(f"开始解压 {os.path.normpath(path)} 到 {out_dir}")
    extract_archive(path, out_dir)
