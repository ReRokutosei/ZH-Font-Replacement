import datetime
import logging
import os
import shutil

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

# 目录创建

def create_directories(config):
    for d in [config.get('TEMP_DIR', './temp'), config.get('RESULT_DIR', './result'), config.get('SOURCE_FILES_DIR', './source_files')]:
        d = os.path.normpath(d)
        if not os.path.exists(d):
            os.makedirs(d)

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
    report_lines.append(f"生成时间: {now_format}")

    # 源字体包版本信息
    report_lines.append("")
    report_lines.append("源字体包版本信息：")
    # Sarasa 版本
    try:
        from fetch_sarasa import get_version_and_assets
        sarasa_version, _ = get_version_and_assets()
        if sarasa_version:
            report_lines.append(f"  Sarasa Gothic: {sarasa_version}")
    except Exception as e:
        report_lines.append(f"  Sarasa Gothic: 获取失败 ({e})")
    # Inter 版本
    try:
        from fetch_inter import get_inter_version_and_assets
        inter_version, _ = get_inter_version_and_assets()
        if inter_version:
            report_lines.append(f"  Inter: {inter_version}")
    except Exception as e:
        report_lines.append(f"  Inter: 获取失败 ({e})")

    report_path = os.path.join(full, "version_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))    
    report_lines.append("主要配置参数说明：")
    explain_map = {
        'ENABLE_MS_YAHEI': '生成微软雅黑字体',
        'ENABLE_SEGOE_UI': '生成Segoe UI字体',
        'SARASA_VERSION_STYLE': 'Sarasa 包类型',
        'MS_YAHEI_NUMERALS_STYLE': '微软雅黑数字风格',
        'SEGOE_UI_SPACING_STYLE': 'Segoe UI 间距风格',
        'DOWNLOAD_MODE': '字体源文件获取方式',
        'TEMP_DIR': '临时文件目录',
        'RESULT_DIR': '结果输出目录',
        'SOURCE_FILES_DIR': '源文件存放目录',
        'CLEAN_TEMP_ON_SUCCESS': '清理临时目录',
    }
    for k, v in config.items():
        if k in explain_map:
            if k == 'ENABLE_MS_YAHEI' or k == 'ENABLE_SEGOE_UI':
                v_str = '启用' if v else '禁用'
            elif k == 'SARASA_VERSION_STYLE':
                v_str = 'hinted' if v == 'hinted' else 'unhinted'
            elif k == 'MS_YAHEI_NUMERALS_STYLE':
                v_str = '等宽(monospaced)' if v == 'monospaced' else '不等宽(proportional)'
            elif k == 'SEGOE_UI_SPACING_STYLE':
                v_str = '宽松(loose)' if v == 'loose' else '紧凑(compact)'
            elif k == 'CLEAN_TEMP_ON_SUCCESS':
                v_str = '是' if v else '否'
            elif k == 'DOWNLOAD_MODE':
                v_str = '本地(local)' if v == 'local' else f'在线({v})'
            else:
                v_str = str(v)
            report_lines.append(f"  {explain_map[k]}：{v_str}")

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
