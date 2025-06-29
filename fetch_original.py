import shutil as fs
import config_utils
import os
import json
import logging
try:
    import requests as req
    from requests.exceptions import RequestException
    import py7zr as sz
    import wget
except ImportError as e:
    logging.error(f"缺少必要的依赖包: {str(e)}")
    logging.error("请使用 pip install requests py7zr wget 安装所需依赖")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

API_URL = 'https://api.github.com/repos/be5invis/Sarasa-Gothic/releases/latest'
config = config_utils.load_config()

def find_local_package():
    """查找本地目标源文件包（只关注 SC UI 和 Mono SC）"""
    if not os.path.exists(config.get('SOURCE_FILES_DIR', './source_files')):
        return None
    files = os.listdir(config.get('SOURCE_FILES_DIR', './source_files'))
    # 优先顺序：UiSC-hint, UiSC-unhint, MonoSC-hint, MonoSC-unhint
    version = None
    # 尝试从网络获取最新版本号
    try:
        response = req.get(API_URL, timeout=config.get('DOWNLOAD_TIMEOUT', 10))
        details = json.loads(response.content)
        version = details['tag_name'][1:]
    except Exception:
        pass
    candidates = []
    if version:
        candidates = [
            f'SarasaUiSC-TTF-{version}.7z',
            f'SarasaUiSC-TTF-Unhinted-{version}.7z',
            f'SarasaMonoSC-TTF-{version}.7z',
            f'SarasaMonoSC-TTF-Unhinted-{version}.7z',
        ]
    else:
        # 兜底：只要名字前缀匹配即可
        for file in files:
            if file.startswith('SarasaUiSC-TTF-') or file.startswith('SarasaMonoSC-TTF-'):
                candidates.append(file)
    for name in candidates:
        if name in files:
            return os.path.join(config.get('SOURCE_FILES_DIR', './source_files'), name)
    return None


def find_all_local_packages():
    """查找本地所有目标源文件包（UiSC/MonoSC）"""
    if not os.path.exists(config.get('SOURCE_FILES_DIR', './source_files')):
        return []
    files = os.listdir(config.get('SOURCE_FILES_DIR', './source_files'))
    version = None
    try:
        import requests as req
        response = req.get(API_URL, timeout=config.get('DOWNLOAD_TIMEOUT', 10))
        details = json.loads(response.content)
        version = details['tag_name'][1:]
    except Exception:
        pass
    candidates = []
    if version:
        candidates = [
            f'SarasaUiSC-TTF-{version}.7z',
            f'SarasaUiSC-TTF-Unhinted-{version}.7z',
            f'SarasaMonoSC-TTF-{version}.7z',
            f'SarasaMonoSC-TTF-Unhinted-{version}.7z',
        ]
        return [os.path.join(config.get('SOURCE_FILES_DIR', './source_files'), name) for name in candidates if name in files]
    else:
        return [os.path.join(config.get('SOURCE_FILES_DIR', './source_files'), file) for file in files if file.startswith('SarasaUiSC-TTF-') or file.startswith('SarasaMonoSC-TTF-')]

def get_latest():
    """获取最新版本下载链接，只关注目标包"""
    if config.get('DOWNLOAD_MODE', 'local') == 'local':
        logging.info("使用本地文件模式")
        local_file = find_local_package()
        if local_file:
            return 'file://' + local_file
        raise Exception("未找到本地源文件包，请检查 source_files 目录")

    try:
        response = req.get(API_URL, timeout=config.get('DOWNLOAD_TIMEOUT', 10))
        details = json.loads(response.content)
        version = details['tag_name'][1:]
        # 只关注这四个目标包
        candidates = [
            f'SarasaUiSC-TTF-{version}.7z',
            f'SarasaUiSC-TTF-Unhinted-{version}.7z',
            f'SarasaMonoSC-TTF-{version}.7z',
            f'SarasaMonoSC-TTF-Unhinted-{version}.7z',
        ]
        assets = details['assets']
        for candidate in candidates:
            for asset in assets:
                if asset['name'] == candidate:
                    return asset['browser_download_url']
    except RequestException as e:
        logging.warning(f"网络下载失败: {str(e)}")
        if config.get('DOWNLOAD_MODE', 'auto') == 'auto':
            logging.info("尝试使用本地文件")
            local_file = find_local_package()
            if local_file:
                return 'file://' + local_file
        raise Exception("无法获取字体包：网络下载失败，且未找到本地源文件")


def get_all_latest():
    """获取所有最新版本下载链接，只关注目标包"""
    try:
        import requests as req
        from requests.exceptions import RequestException
        response = req.get(API_URL, timeout=config.get('DOWNLOAD_TIMEOUT', 10))
        details = json.loads(response.content)
        version = details['tag_name'][1:]
        candidates = [
            f'SarasaUiSC-TTF-{version}.7z',
            f'SarasaUiSC-TTF-Unhinted-{version}.7z',
            f'SarasaMonoSC-TTF-{version}.7z',
            f'SarasaMonoSC-TTF-Unhinted-{version}.7z',
        ]
        assets = details['assets']
        urls = []
        for candidate in candidates:
            for asset in assets:
                if asset['name'] == candidate:
                    urls.append(asset['browser_download_url'])
        return urls
    except Exception:
        return []


def clear_dir(directory):
    if (os.path.exists(directory)):
        fs.rmtree(directory)
    os.makedirs(directory)


def download(url, save_dir=None):
    """下载文件，支持本地文件和网络下载，支持自定义保存目录。若本地已存在同名最新文件则跳过下载，若为旧版本则删除后下载新版本。"""
    if save_dir is None:
        save_dir = config.get('TEMP_DIR', './temp')
    filename = url.split('/')[-1]
    target_path = os.path.join(save_dir, filename)
    # 在线下载时，若本地已存在同名文件则跳过
    if url.startswith('http'):
        if os.path.exists(target_path):
            # 检查是否为最新版本（文件名包含版本号，若一致即为最新）
            return target_path
        # 删除旧版本（同前缀不同版本）
        prefix = filename.split('-')[0]
        for f in os.listdir(save_dir):
            if f.startswith(prefix) and f != filename:
                os.remove(os.path.join(save_dir, f))
    if url.startswith('file://'):
        local_path = url[7:]
        if os.path.exists(local_path):
            fs.copy(local_path, target_path)
            return target_path
        raise Exception(f"本地文件不存在: {local_path}")
    try:
        import requests as req
        logging.info(f"开始下载文件: {filename}")
        response = req.get(url, timeout=config.get('DOWNLOAD_TIMEOUT', 10), stream=True)
        total_size = int(response.headers.get('content-length', 0))
        with open(target_path, 'wb') as f:
            if total_size == 0:
                f.write(response.content)
            else:
                downloaded = 0
                for data in response.iter_content(chunk_size=4096):
                    downloaded += len(data)
                    f.write(data)
                    done = int(50 * downloaded / total_size)
                    print(f"\r下载进度: [{'=' * done}{' ' * (50-done)}] {downloaded}/{total_size} bytes", end='')
        print()
        logging.info(f"文件下载完成: {filename}")
        return target_path
    except Exception as e:
        logging.error(f"下载失败: {str(e)}")
        raise


def unzip(path):
    """解压7z文件"""
    try:
        logging.info(f"开始解压文件: {path}")
        with sz.SevenZipFile(path, mode='r') as zip_file:
            zip_file.extractall(path=config.get('TEMP_DIR', './temp'))
        logging.info("文件解压完成")
    except Exception as e:
        logging.error(f"解压失败: {str(e)}")
        raise
