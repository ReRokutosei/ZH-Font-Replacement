import datetime
import logging
import os
import shutil
import subprocess
import time
import zipfile

import py7zr as sz
import yaml
from otf2ttf.official.otf2ttf import otf_to_ttf as official_otf2ttf, update_hmtx, TTFont, MAX_ERR, POST_FORMAT, REVERSE_DIRECTION


# 配置加载
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path, encoding='utf-8') as f:
        config = yaml.safe_load(f)
    if not isinstance(config, dict):
        raise RuntimeError(f"config.yaml 解析异常，返回类型: {type(config)}, 内容: {config}")
    return config

# 配置校验
def validate_config(config):
    if not config.get('ENABLE_MS_YAHEI', True) and not config.get('ENABLE_SEGOE_UI', True):
        logging.error("错误：至少需要启用一项生成功能（微软雅黑/Segoe UI）")
        raise SystemExit(1)


# 通用目录创建
def ensure_dir_exists(path):
    """
    确保目录存在，不存在则创建。
    """
    path = os.path.normpath(path)
    if not os.path.exists(path):
        os.makedirs(path)

# 目录创建
def create_directories(config):
    for d in [config.get('TEMP_DIR', './temp'), config.get('RESULT_DIR', './result'), config.get('SOURCE_FILES_DIR', './source_files')]:
        ensure_dir_exists(d)
# 通用解压缩
def extract_archive(archive_path, out_dir):
    """
    自动判断 zip/7z 并解压到 out_dir。
    """
    ext = os.path.splitext(archive_path)[1].lower()
    ensure_dir_exists(out_dir)
    if ext == '.zip':
        with zipfile.ZipFile(archive_path, 'r') as zf:
            zf.extractall(out_dir)
    elif ext == '.7z':
        with sz.SevenZipFile(archive_path, mode='r') as archive:
            archive.extractall(path=out_dir)
    else:
        raise RuntimeError(f"仅支持 zip/7z 格式，错误文件: {archive_path}")

# 通用安全拷贝
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

# 通用进度条输出
def print_progress_bar(current, total, prefix='', suffix='', length=40):
    """
    打印进度条到控制台。
    """
    percent = f"{100 * (current / float(total)):.1f}" if total else '0.0'
    filled_length = int(length * current // total) if total else 0
    bar = '█' * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='')
    if current >= total:
        print()

# 配置参数获取（带默认值）
def get_config_value(config, key, default=None):
    """
    获取配置参数，若不存在则返回默认值。
    """
    return config[key] if key in config else default


# 通用字体文件查找
def find_font_file(root_dir, target_name):
    """
    在 root_dir 下递归查找名为 target_name 的文件，返回相对路径（相对于 root_dir）。
    若未找到则抛出 FileNotFoundError。
    """
    # 防御性：只允许普通文件名，防止特殊字符
    if not isinstance(target_name, str) or any(c in target_name for c in r"/\\:*?\"<>|"):
        raise ValueError(f"非法文件名: {target_name}")
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname == target_name:
                rel_path = os.path.relpath(os.path.join(dirpath, fname), root_dir)
                return rel_path
    raise FileNotFoundError(f"未在 {root_dir} 下找到目标文件: {target_name}")


# OTF 批量转 TTF（依赖 otf2ttf 命令行工具）
def find_otf_files(root_dir):
    """
    递归查找 root_dir 下所有 .otf 文件，返回绝对路径列表。
    """
    otf_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith('.otf'):
                otf_files.append(os.path.join(dirpath, filename))
    return otf_files

def convert_otf_to_ttf(otf_path, verbose=False):
    """
    使用官方实现将单个 OTF 文件转为 TTF。
    返回 (success: bool, duration: float)
    """
    start = time.time()
    try:
        # 直接调用官方FontTools的otf2ttf实现
        logging.info(f"[OTF2TTF] 开始转换: {os.path.basename(otf_path)}")
        font = TTFont(otf_path)
        official_otf2ttf(font, max_err=MAX_ERR)
        # 更新hmtx表
        update_hmtx(font, font["glyf"])
        ttf_path = os.path.splitext(otf_path)[0] + '.ttf'
        font.save(ttf_path)
        logging.info(f"[OTF2TTF] 转换完成: {os.path.basename(ttf_path)}")
        success = True
    except Exception as e:
        logging.error(f"转换失败: {otf_path} 异常: {str(e)}")
        success = False
    end = time.time()
    return success, end - start

def batch_convert_otf_to_ttf(root_dir, verbose=True, target_files=None):
    """
    批量转换 OTF 文件为 TTF。
    root_dir: 根目录
    verbose: 是否详细输出
    target_files: 指定要转换的文件列表（绝对路径），为 None 时转换目录下所有 OTF 文件
    返回转换成功的 TTF 文件路径列表。
    """
    if target_files is None:
        otf_files = find_otf_files(root_dir)
    else:
        # 只转换指定的文件
        otf_files = [f for f in target_files if f.lower().endswith('.otf')]
    
    total = len(otf_files)
    if total == 0:
        if verbose:
            logging.info("没有找到需要转换的 OTF 文件")
        return []
    
    if verbose:
        logging.info(f"共找到 {total} 个 OTF 文件，开始转换...")
    ttf_files = []
    global_start = time.time()
    for idx, otf_file in enumerate(otf_files, 1):
        if verbose:
            logging.info(f"[{idx}/{total}] 正在转换: {os.path.basename(otf_file)}")
        success, duration = convert_otf_to_ttf(otf_file, verbose=verbose)
        ttf_path = os.path.splitext(otf_file)[0] + '.ttf'
        if success and os.path.exists(ttf_path):
            ttf_files.append(ttf_path)
            if verbose:
                logging.info(f"转换完成，用时 {duration:.2f} 秒")
        else:
            if verbose:
                logging.error(f"转换失败，用时 {duration:.2f} 秒")
    global_end = time.time()
    if verbose:
        logging.info(f"OTF全部转换完成，总用时 {global_end - global_start:.2f} 秒")
    return ttf_files


def update_mapping_otf_to_ttf(mapping, temp_dir, verbose=True):
    """
    检查 mapping 中的 .otf 文件，自动批量转为 .ttf，并返回新 mapping（全部为 ttf 文件名）。
    mapping: list 或 dict，元素为 (dst, src) 或 {dst: src}
    temp_dir: 解压后字体所在目录
    """
    # 统一为 list[(dst, src)]
    if isinstance(mapping, dict):
        items = list(mapping.items())
    else:
        items = list(mapping)

    # 收集所有需要转换的 otf 文件名，去重
    otf_set = set()
    otf_path_map = dict()
    for _, src in items:
        if src.lower().endswith('.otf'):
            try:
                rel_path = find_font_file(temp_dir, src)
                otf_path = os.path.join(temp_dir, rel_path)
                otf_set.add(otf_path)
                otf_path_map[src] = otf_path
            except Exception:
                msg = f"未找到 OTF 文件: {src} (在 {temp_dir} 及其子目录)"
                if verbose:
                    logging.error(msg)
                raise RuntimeError(msg)
    
    # 使用批量转换函数处理所有 OTF 文件
    if otf_set:
        if verbose:
            logging.info(f"发现 {len(otf_set)} 个 OTF 文件需要转换")
        try:
            batch_convert_otf_to_ttf(temp_dir, verbose=verbose, target_files=list(otf_set))
        except Exception as e:
            msg = f"批量 OTF 转 TTF 失败: {e}"
            if verbose:
                logging.error(msg)
            raise RuntimeError(msg)
    
    new_mapping = []
    for dst, src in items:
        if src.lower().endswith('.otf'):
            ttf_src = os.path.splitext(src)[0] + '.ttf'
            new_mapping.append((dst, ttf_src))
        else:
            new_mapping.append((dst, src))
    return new_mapping


# 结果目录和报告
def get_new_result_dir(config):
    now = datetime.datetime.now()
    now_dir = now.strftime('%Y%m%d%H%M')
    now_format = now.strftime('%Y年%m月%d日 %H:%M:%S')
    base = config.get('RESULT_DIR', './result')
    exist = [x for x in os.listdir(base) if x.startswith('ver') and os.path.isdir(os.path.join(base, x))]
    nums = [int(x[3:5]) for x in exist if x[3:5].isdigit()]
    num = max(nums) + 1 if nums else 1
    subdir = f'ver{num:02d}-{now_dir}'
    full = os.path.join(base, subdir)
    os.makedirs(full, exist_ok=True)
    write_version_report(config, now_format, full)
    return full

def write_version_report(config, now_format, full):
    report_lines = []

    # 生成时间
    report_lines.append(f"生成时间: {now_format}")

    # 源字体包版本信息
    report_lines.extend(["", "源字体包版本信息："])
    if config.get('FONT_PACKAGE_SOURCE', 'local') == 'custom':
        # custom 模式下仅写入自定义字体包文件名（支持单个或多个）
        if config.get('ENABLE_MS_YAHEI', True):
            ms_pkg = config.get('CUSTOM_MS_YAHEI_PACKAGE', '')
            if ms_pkg:
                if isinstance(ms_pkg, list):
                    for i, pkg in enumerate(ms_pkg, 1):
                        report_lines.append(f"  MSYH 字体包[{i}]: {pkg}")
                else:
                    report_lines.append(f"  MSYH 字体包: {ms_pkg}")
        if config.get('ENABLE_SEGOE_UI', True):
            se_pkg = config.get('CUSTOM_SEGOE_PACKAGE', '')
            if se_pkg:
                if isinstance(se_pkg, list):
                    for i, pkg in enumerate(se_pkg, 1):
                        report_lines.append(f"  Segoe UI 字体包[{i}]: {pkg}")
                else:
                    report_lines.append(f"  Segoe UI 字体包: {se_pkg}")
    else:
        # Sarasa 版本
        if config.get('ENABLE_MS_YAHEI', True):
            try:
                from fetch_sarasa import get_version_and_assets
                sarasa_version, _ = get_version_and_assets()
                if sarasa_version:
                    report_lines.append(f"  Sarasa Gothic: {sarasa_version}")
            except Exception as e:
                report_lines.append(f"  Sarasa Gothic: 获取失败 ({e})")

        # Inter 版本
        if config.get('ENABLE_SEGOE_UI', True):
            try:
                from fetch_inter import get_inter_version_and_assets
                inter_version, _ = get_inter_version_and_assets(silent=True)
                if inter_version:
                    report_lines.append(f"  Inter: {inter_version}")
            except Exception as e:
                report_lines.append(f"  Inter: 获取失败 ({e})")

    # 主要配置参数说明
    report_lines.append("主要配置参数说明：")

    if config.get('FONT_PACKAGE_SOURCE', 'custom') == 'custom':
        explain_map = {
            'ENABLE_MS_YAHEI': '生成微软雅黑字体',
            'ENABLE_SEGOE_UI': '生成Segoe UI字体',
            'FONT_PACKAGE_SOURCE': '字体源文件获取方式',
            'TEMP_DIR': '临时文件目录',
            'RESULT_DIR': '结果输出目录',
            'SOURCE_FILES_DIR': '源文件存放目录',
            'CLEAN_TEMP_ON_SUCCESS': '清理临时目录',
        }
    else:
        explain_map = {
            'ENABLE_MS_YAHEI': '生成微软雅黑字体',
            'ENABLE_SEGOE_UI': '生成Segoe UI字体',
            'SARASA_VERSION_STYLE': 'Sarasa 包类型',
            'MS_YAHEI_NUMERALS_STYLE': '微软雅黑数字风格',
            'SEGOE_UI_SPACING_STYLE': 'Segoe UI 间距风格',
            'FONT_PACKAGE_SOURCE': '字体源文件获取方式',
            'TEMP_DIR': '临时文件目录',
            'RESULT_DIR': '结果输出目录',
            'SOURCE_FILES_DIR': '源文件存放目录',
            'CLEAN_TEMP_ON_SUCCESS': '清理临时目录',
        }
    for k, v in config.items():
        if k in explain_map:
            if k in ['ENABLE_MS_YAHEI', 'ENABLE_SEGOE_UI']:
                v_str = '启用' if v else '禁用'
            elif k == 'CLEAN_TEMP_ON_SUCCESS':
                v_str = '是' if v else '否'
            elif k == 'FONT_PACKAGE_SOURCE':
                if v == 'local':
                    v_str = '本地(local)'
                elif v == 'online':
                    v_str = '在线(online)'
                elif v == 'custom':
                    v_str = '自定义(custom)'
                else:
                    v_str = str(v)
            else:
                v_str = str(v)
            report_lines.append(f"  {explain_map[k]}: {v_str}")

    # 写入文件
    report_path = os.path.join(full, "version_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))


# 解压自定义字体包（ custom 模式调用）
def extract_custom_font_packages(config):
    """
    解压 config.yaml 中指定的 CUSTOM_MS_YAHEI_PACKAGE 和 CUSTOM_SEGOE_PACKAGE 到 TEMP_DIR。
    仅支持 zip/7z 格式。
    """
    source_dir = os.path.abspath(config.get('SOURCE_FILES_DIR', './source_files'))
    temp_dir = os.path.abspath(config.get('TEMP_DIR', './temp'))
    os.makedirs(temp_dir, exist_ok=True)
    def extract_font_package(pkg_item):
        pkg_path = pkg_item if os.path.isabs(pkg_item) else os.path.join(source_dir, pkg_item)
        pkg_path = os.path.abspath(pkg_path)
        if not os.path.isfile(pkg_path):
            raise RuntimeError(f"自定义字体包不存在: {pkg_path}")
        ext = os.path.splitext(pkg_path)[1].lower()
        if ext == '.zip':
            # 始终用zipfile并强制用gbk修正文件名，兼容所有中文zip
            with zipfile.ZipFile(pkg_path, 'r') as zf:
                for info in zf.infolist():
                    name = info.filename
                    try:
                        name_gbk = name.encode('cp437').decode('gbk')
                    except Exception:
                        name_gbk = name
                    target_path = os.path.join(temp_dir, name_gbk)
                    if info.is_dir():
                        os.makedirs(target_path, exist_ok=True)
                    else:
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        with zf.open(info) as src, open(target_path, 'wb') as dst:
                            dst.write(src.read())
        elif ext == '.7z':
            with sz.SevenZipFile(pkg_path, mode='r') as archive:
                archive.extractall(path=temp_dir)
        else:
            raise RuntimeError(f"仅支持 zip/7z 格式，自定义字体包错误: {pkg_path}")

    if config.get('ENABLE_MS_YAHEI', True):
        ms_pkg = config.get('CUSTOM_MS_YAHEI_PACKAGE', '')
        if not ms_pkg:
            raise RuntimeError("未指定自定义中文字体包路径 (config.yaml)")
        if isinstance(ms_pkg, list):
            for pkg in ms_pkg:
                extract_font_package(pkg)
        else:
            extract_font_package(ms_pkg)
    if config.get('ENABLE_SEGOE_UI', True):
        se_pkg = config.get('CUSTOM_SEGOE_PACKAGE', '')
        if not se_pkg:
            raise RuntimeError("未指定自定义英文字体包路径 (config.yaml)")
        if isinstance(se_pkg, list):
            for pkg in se_pkg:
                extract_font_package(pkg)
        else:
            extract_font_package(se_pkg)


# 清理临时目录
def clean_temp_dir(config):
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
