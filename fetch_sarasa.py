import os
import json
import logging
import yaml
import requests as req
import py7zr as sz


config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
with open(config_path, encoding='utf-8') as f:
    config = yaml.safe_load(f)
if not isinstance(config, dict):
    raise RuntimeError(f"config.yaml 解析异常，返回类型: {type(config)}, 内容: {config}")

API_URL = 'https://api.github.com/repos/be5invis/Sarasa-Gothic/releases/latest'

def get_version_and_assets():
    try:
        response = req.get(API_URL, timeout=config.get('DOWNLOAD_TIMEOUT', 10))
        details = json.loads(response.content)
        version = details['tag_name'][1:]
        assets = details.get('assets', [])
        return version, assets
    except Exception:
        return None, []

def get_candidates(version):
    sarasa_version = config.get('SARASA_VERSION', 'normal')
    candidates = []
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
    dir_ = os.path.normpath(config.get('SOURCE_FILES_DIR', './source_files'))
    if not os.path.exists(dir_):
        return []
    files = os.listdir(dir_)
    version, _ = get_version_and_assets()
    candidates = get_candidates(version) if version else []
    if not candidates:
        for file in files:
            if file.startswith('SarasaUiSC-TTF-') or file.startswith('SarasaMonoSC-TTF-'):
                candidates.append(file)
    return [os.path.normpath(os.path.join(dir_, name)) for name in candidates if name in files]

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
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    filename = url.split('/')[-1]
    target_path = os.path.normpath(os.path.join(save_dir, filename))
    if os.path.exists(target_path):
        return target_path
    resp = req.get(url, stream=True)
    with open(target_path, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return target_path

def unzip(path):
    out_dir = os.path.normpath(config.get('TEMP_DIR', './temp'))
    logging.info(f"开始解压 {os.path.normpath(path)} 到 {out_dir}")
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    with sz.SevenZipFile(path, mode='r') as z:
        z.extractall(path=out_dir)
