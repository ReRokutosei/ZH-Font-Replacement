import datetime
import logging
import os
import shutil
import zipfile

import py7zr as sz
import yaml


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
        # custom 模式下仅写入自定义字体包文件名
        if config.get('ENABLE_MS_YAHEI', True):
            ms_pkg = config.get('CUSTOM_MS_YAHEI_PACKAGE', '')
            if ms_pkg:
                report_lines.append(f"  MSYH 字体包: {ms_pkg}")
        if config.get('ENABLE_SEGOE_UI', True):
            se_pkg = config.get('CUSTOM_SEGOE_PACKAGE', '')
            if se_pkg:
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
    def extract_font_package(pkg_name, desc):
        if not pkg_name:
            raise RuntimeError(f"未指定{desc}自定义字体包路径 (config.yaml)")
        pkg_path = pkg_name if os.path.isabs(pkg_name) else os.path.join(source_dir, pkg_name)
        pkg_path = os.path.abspath(pkg_path)
        if not os.path.isfile(pkg_path):
            raise RuntimeError(f"自定义字体包不存在: {pkg_path}")
        ext = os.path.splitext(pkg_path)[1].lower()
        if ext == '.zip':
            with zipfile.ZipFile(pkg_path, 'r') as zf:
                zf.extractall(temp_dir)
        elif ext == '.7z':
            with sz.SevenZipFile(pkg_path, mode='r') as archive:
                archive.extractall(path=temp_dir)
        else:
            raise RuntimeError(f"仅支持 zip/7z 格式，自定义字体包错误: {pkg_path}")

    if config.get('ENABLE_MS_YAHEI', True):
        extract_font_package(config.get('CUSTOM_MS_YAHEI_PACKAGE', ''), True)
    if config.get('ENABLE_SEGOE_UI', True):
        extract_font_package(config.get('CUSTOM_SEGOE_PACKAGE', ''), True)


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
