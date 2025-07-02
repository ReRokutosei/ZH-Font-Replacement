import json
import logging
import os
import sys
import time
import zipfile

import requests as req
import yaml

config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
with open(config_path, encoding='utf-8') as f:
    config = yaml.safe_load(f)

SOURCE_FILES_DIR = config.get('SOURCE_FILES_DIR', './source_files')
TEMP_DIR = config.get('TEMP_DIR', './temp')

INTER_API_URL = 'https://api.github.com/repos/rsms/inter/releases/latest'

# 全局缓存
_inter_version_cache = None

def get_inter_version_and_assets():
    """在线获取 Inter 最新版本信息"""
    global _inter_version_cache
    if _inter_version_cache is not None:
        return _inter_version_cache
    try:
        response = req.get(INTER_API_URL, timeout=config.get('DOWNLOAD_TIMEOUT', 10))
        details = response.json()
        version = details['tag_name']
        assets = details.get('assets', [])
        logging.info(f"获取 Inter 在线版本信息成功: {version}")
        _inter_version_cache = (version, assets)
        return version, assets
    except Exception as e:
        logging.error(f"获取 Inter 在线版本信息失败: {e}")
        _inter_version_cache = (None, [])
        return None, []

def find_local_inter_zip():
    dir_ = os.path.normpath(SOURCE_FILES_DIR)
    if not os.path.exists(dir_):
        return None
    files = os.listdir(dir_)
    zips = [f for f in files if f.startswith('Inter-') and f.endswith('.zip')]
    if not zips:
        return None
    zips.sort(reverse=True)
    return os.path.normpath(os.path.join(dir_, zips[0]))

def get_latest_inter_zip_url():
    try:
        response = req.get(INTER_API_URL, timeout=config.get('DOWNLOAD_TIMEOUT', 10))  # 兼容老逻辑，后续可重构
        releases = json.loads(response.content)
        for release in releases:
            if release.get('draft') or release.get('prerelease'):
                continue
            assets = release.get('assets', [])
            for asset in assets:
                name = asset.get('name', '')
                if name.startswith('Inter-') and name.endswith('.zip'):
                    return asset.get('browser_download_url')
    except Exception as e:
        logging.error(f"获取 Inter Releases 失败: {str(e)}")
    return None

def download(url, save_dir=None):
    if save_dir is None:
        save_dir = SOURCE_FILES_DIR
    save_dir = os.path.normpath(save_dir)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    filename = url.split('/')[-1]
    target_path = os.path.normpath(os.path.join(save_dir, filename))
    if os.path.exists(target_path):
        return target_path
    
    resp = req.get(url, timeout=config.get('DOWNLOAD_TIMEOUT', 10), stream=True)
    total_size = int(resp.headers.get('content-length', 0))
    downloaded_size = 0
    start_time = time.time()
    
    with open(target_path, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded_size += len(chunk)
                
                # 进度输出
                progress = downloaded_size / total_size if total_size > 0 else 0
                duration = time.time() - start_time
                speed = downloaded_size / duration if duration > 0 else 0
                
                sys.stdout.write(f'\r下载进度: {downloaded_size}/{total_size} 字节 ({progress:.2%}) | 速度: {speed/1024:.2f} KB/s')
                sys.stdout.flush()
    
    return target_path

def unzip_inter(path, out_dir=None):
    if out_dir is None:
        out_dir = TEMP_DIR
    out_dir = os.path.normpath(out_dir)
    logging.info(f"开始解压 {os.path.normpath(path)} 到 {out_dir}")
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(out_dir)

def fetch_inter():
    local_zip = find_local_inter_zip()
    if local_zip:
        logging.info(f"已存在本地 Inter 包，跳过下载: {os.path.basename(local_zip)}")
        unzip_inter(local_zip)
        return local_zip
    url = get_latest_inter_zip_url()
    if not url:
        raise Exception("未找到 Inter 最新 zip 包的下载链接")
    logging.info(f"下载 Inter 包: {url}")
    zip_path = download(url)
    unzip_inter(zip_path)
    return zip_path

if __name__ == '__main__':
    fetch_inter()
