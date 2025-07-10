import json
import logging
import os

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._n_a_m_e import NameRecord

from utils.config import get_config_value, load_config
from utils.file_ops import find_font_file, safe_copy
from utils.progress import print_progress_bar

# 加载配置
config = load_config()

# 宽松间距映射表
SEGOE_MAPPING_LOOSE = [
    ("segoeui.ttf", "Inter-Regular.ttf"),
    ("segoeuib.ttf", "Inter-Bold.ttf"),
    ("segoeuii.ttf", "Inter-Italic.ttf"),
    ("segoeuil.ttf", "Inter-Thin.ttf"),
    ("segoeuisl.ttf", "Inter-Light.ttf"),
    ("segoeuiz.ttf", "Inter-BoldItalic.ttf"),
    ("seguibl.ttf", "Inter-Black.ttf"),
    ("seguibli.ttf", "Inter-BlackItalic.ttf"),
    ("seguili.ttf", "Inter-ThinItalic.ttf"),
    ("seguisb.ttf", "Inter-SemiBold.ttf"),
    ("seguisbi.ttf", "Inter-SemiBoldItalic.ttf"),
    ("seguisli.ttf", "Inter-LightItalic.ttf"),
]

# 紧凑间距映射表
SEGOE_MAPPING_COMPACT = [
    ("segoeui.ttf", "InterDisplay-Regular.ttf"),
    ("segoeuib.ttf", "InterDisplay-Bold.ttf"),
    ("segoeuii.ttf", "InterDisplay-Italic.ttf"),
    ("segoeuil.ttf", "InterDisplay-Thin.ttf"),
    ("segoeuisl.ttf", "InterDisplay-Light.ttf"),
    ("segoeuiz.ttf", "InterDisplay-BoldItalic.ttf"),
    ("seguibl.ttf", "InterDisplay-Black.ttf"),
    ("seguibli.ttf", "InterDisplay-BlackItalic.ttf"),
    ("seguili.ttf", "InterDisplay-ThinItalic.ttf"),
    ("seguisb.ttf", "InterDisplay-SemiBold.ttf"),
    ("seguisbi.ttf", "InterDisplay-SemiBoldItalic.ttf"),
    ("seguisli.ttf", "InterDisplay-LightItalic.ttf"),
]


def get_segoe_mapping():
    """获取Segoe UI字体映射表"""
    # 支持 custom 模式
    if get_config_value(config, "FONT_PACKAGE_SOURCE", "local") == "custom":
        mapping = get_config_value(config, "segoe_mapping", [])
        if isinstance(mapping, dict):
            return list(mapping.items())
        return [tuple(x) for x in mapping]
    style = get_config_value(config, "SEGOE_UI_SPACING_STYLE", "loose").lower()
    if style == "compact":
        return SEGOE_MAPPING_COMPACT
    return SEGOE_MAPPING_LOOSE


def copy_font_info(dst, info_json):
    """复制字体信息到目标文件"""
    try:
        font = TTFont(dst)
        name_table = font["name"]
        name_table.names.clear()
        for field in info_json.get("name_fields", []):
            parts = dict(
                item.strip().split("=", 1) for item in field.split(",") if "=" in item
            )
            rec = NameRecord()
            rec.nameID = int(parts.get("NameID", 0))
            rec.platformID = int(parts.get("Platform", 3))
            rec.platEncID = int(parts.get("Encoding", 1))
            rec.langID = int(parts.get("Lang", 0))
            rec.string = parts.get("Value", "").encode("utf-16-be")
            name_table.names.append(rec)
        font.save(dst)
    except Exception as e:
        logging.error(f"设置字体信息失败: {dst}")
        raise RuntimeError(f"设置字体信息失败: {dst}") from e


def load_font_info():
    """加载字体信息文件"""
    font_info_path = os.path.join(
        os.path.dirname(__file__), "font_info", "segoe_font_info.json"
    )
    try:
        with open(font_info_path, "r", encoding="utf-8") as f:
            infos = json.load(f)
        return {info["file"].lower(): info for info in infos}
    except FileNotFoundError:
        logging.error(f"字体信息文件不存在: {font_info_path}")
        raise RuntimeError(
            "缺少必需的字体信息文件，请确保 font_info/segoe_font_info.json 存在"
        ) from None
    except json.JSONDecodeError as e:
        logging.error(f"字体信息文件格式错误: {font_info_path}")
        raise RuntimeError(f"字体信息文件解析失败: {e}") from None


def batch_rename_and_patch():
    """批量重命名和修补字体文件"""
    info_map = load_font_info()
    mapping = get_segoe_mapping()
    temp_dir = get_config_value(config, "TEMP_DIR", "./temp")

    total = len(mapping)
    if total == 0:
        raise RuntimeError("Segoe UI字体映射表为空，请检查配置")

    logging.info(f"开始处理 {total} 个 Segoe UI 字体文件")
    processed_count = 0

    for idx, (segoe_name, inter_name) in enumerate(mapping, 1):
        try:
            rel_inter_path = find_font_file(temp_dir, inter_name)
            inter_path = os.path.join(temp_dir, rel_inter_path)
            segoe_out = os.path.join(temp_dir, segoe_name)
            safe_copy(inter_path, segoe_out)

            info = info_map.get(segoe_name.lower())
            if info:
                copy_font_info(segoe_out, info)
            processed_count += 1
            print_progress_bar(
                idx,
                total,
                prefix="处理Segoe UI字体",
                suffix=f"{segoe_name} ({idx}/{total})",
            )
            logging.debug(f"处理成功: {inter_name} -> {segoe_name}")
        except Exception as e:
            print()  # 清理进度条
            logging.error(f"处理失败: {inter_name} -> {segoe_name}, 错误: {e}")
            raise RuntimeError(f"处理字体文件失败: {segoe_name}") from e

    print()  # 进度条完成后换行
    logging.info(f"Segoe UI字体处理完成 - 成功: {processed_count}")


def copy_result_files(result_dir):
    """复制生成的字体文件到结果目录"""
    mapping = get_segoe_mapping()
    total = len(mapping)
    if total == 0:
        raise RuntimeError("Segoe UI字体映射表为空，请检查配置")

    logging.info(f"开始复制 {total} 个 Segoe UI 字体文件到结果目录")
    copied_count = 0

    for idx, (segoe_name, _) in enumerate(mapping, 1):
        try:
            src = os.path.join(
                get_config_value(config, "TEMP_DIR", "./temp"), segoe_name
            )
            dst = os.path.join(result_dir, segoe_name)
            safe_copy(src, dst)
            copied_count += 1
            print_progress_bar(
                idx,
                total,
                prefix="复制Segoe UI字体",
                suffix=f"{segoe_name} ({idx}/{total})",
            )
            logging.debug(f"复制成功: {segoe_name}")
        except Exception as e:
            print()  # 清理进度条
            logging.error(f"复制 {src} 到 {dst} 失败: {e}")
            raise RuntimeError(f"复制字体文件失败: {segoe_name}") from e

    print()  # 进度条完成后换行
    logging.info(f"Segoe UI字体复制完成 - 成功: {copied_count}")


if __name__ == "__main__":
    batch_rename_and_patch()
