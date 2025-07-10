"""
结果管理模块
负责结果目录的创建和版本报告的生成
"""

import datetime
import logging
import os


def get_new_result_dir(config):
    """创建新的结果目录"""
    now = datetime.datetime.now()
    now_dir = now.strftime("%Y%m%d%H%M")
    now_format = now.strftime("%Y年%m月%d日 %H:%M:%S")
    base = config.get("RESULT_DIR", "./result")
    exist = [
        x
        for x in os.listdir(base)
        if x.startswith("ver") and os.path.isdir(os.path.join(base, x))
    ]
    nums = [int(x[3:5]) for x in exist if x[3:5].isdigit()]
    num = max(nums) + 1 if nums else 1
    subdir = f"ver{num:02d}-{now_dir}"
    full = os.path.join(base, subdir)
    os.makedirs(full, exist_ok=True)
    write_version_report(config, now_format, full)
    return full


def write_version_report(config, now_format, full):
    """生成版本报告"""
    report_lines = []

    # 生成时间
    report_lines.append(f"生成时间: {now_format}")

    # 源字体包版本信息
    report_lines.extend(["", "源字体包版本信息："])
    if config.get("FONT_PACKAGE_SOURCE", "local") == "custom":
        # custom 模式下仅写入自定义字体包文件名（支持单个或多个）
        if config.get("ENABLE_MS_YAHEI", True):
            ms_pkg = config.get("CUSTOM_MS_YAHEI_PACKAGE", "")
            if ms_pkg:
                if isinstance(ms_pkg, list):
                    for i, pkg in enumerate(ms_pkg, 1):
                        report_lines.append(f"  MSYH 字体包[{i}]: {pkg}")
                else:
                    report_lines.append(f"  MSYH 字体包: {ms_pkg}")
        if config.get("ENABLE_SEGOE_UI", True):
            se_pkg = config.get("CUSTOM_SEGOE_PACKAGE", "")
            if se_pkg:
                if isinstance(se_pkg, list):
                    for i, pkg in enumerate(se_pkg, 1):
                        report_lines.append(f"  Segoe UI 字体包[{i}]: {pkg}")
                else:
                    report_lines.append(f"  Segoe UI 字体包: {se_pkg}")
    else:
        # Sarasa 版本
        if config.get("ENABLE_MS_YAHEI", True):
            try:
                from fetch_sarasa import get_version_and_assets

                sarasa_version, _ = get_version_and_assets()
                if sarasa_version:
                    report_lines.append(f"  Sarasa Gothic: {sarasa_version}")
            except Exception as e:
                report_lines.append(f"  Sarasa Gothic: 获取失败 ({e})")

        # Inter 版本
        if config.get("ENABLE_SEGOE_UI", True):
            try:
                from fetch_inter import get_inter_version_and_assets

                inter_version, _ = get_inter_version_and_assets(silent=True)
                if inter_version:
                    report_lines.append(f"  Inter: {inter_version}")
            except Exception as e:
                report_lines.append(f"  Inter: 获取失败 ({e})")

    # 主要配置参数说明
    report_lines.append("")
    report_lines.append("主要配置参数说明：")

    if config.get("FONT_PACKAGE_SOURCE", "custom") == "custom":
        explain_map = {
            "ENABLE_MS_YAHEI": "生成微软雅黑字体",
            "ENABLE_SEGOE_UI": "生成Segoe UI字体",
            "FONT_PACKAGE_SOURCE": "字体源文件获取方式",
            "TEMP_DIR": "临时文件目录",
            "RESULT_DIR": "结果输出目录",
            "SOURCE_FILES_DIR": "源文件存放目录",
            "CLEAN_TEMP_ON_SUCCESS": "清理临时目录",
            "MSYH_ENABLE_EXTRA_ITALIC": "微软雅黑额外斜体",
        }
    else:
        explain_map = {
            "ENABLE_MS_YAHEI": "生成微软雅黑字体",
            "ENABLE_SEGOE_UI": "生成Segoe UI字体",
            "SARASA_VERSION_STYLE": "Sarasa 包类型",
            "MS_YAHEI_NUMERALS_STYLE": "微软雅黑数字风格",
            "SEGOE_UI_SPACING_STYLE": "Segoe UI 间距风格",
            "FONT_PACKAGE_SOURCE": "字体源文件获取方式",
            "TEMP_DIR": "临时文件目录",
            "RESULT_DIR": "结果输出目录",
            "SOURCE_FILES_DIR": "源文件存放目录",
            "CLEAN_TEMP_ON_SUCCESS": "清理临时目录",
            "MSYH_ENABLE_EXTRA_ITALIC": "微软雅黑额外斜体",
        }
    for k, v in config.items():
        if k in explain_map:
            if k in ["ENABLE_MS_YAHEI", "ENABLE_SEGOE_UI", "MSYH_ENABLE_EXTRA_ITALIC", "CLEAN_TEMP_ON_SUCCESS"]:
                v_str = "启用" if v else "禁用"
            elif k == "FONT_PACKAGE_SOURCE":
                if v == "local":
                    v_str = "本地(local)"
                elif v == "online":
                    v_str = "在线(online)"
                elif v == "custom":
                    v_str = "自定义(custom)"
                else:
                    v_str = str(v)
            else:
                v_str = str(v)
            report_lines.append(f"  {explain_map[k]}: {v_str}")

    # 写入文件
    report_path = os.path.join(full, "version_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
