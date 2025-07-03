import json
import os
import shutil

import yaml
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._n_a_m_e import NameRecord

from project_utils import find_font_file, load_config, safe_copy

config = load_config()
REF_DIR = os.path.join(config.get('TEMP_DIR', './temp'), 'extras', 'ttf')  # 直接使用解压后的单独ttf目录
DST_DIR = config.get('TEMP_DIR', './temp')
FONT_INFO_DIR = './font_info'


# 宽松间距映射表
SEGOE_MAPPING_LOOSE = [
    ("segoeui.ttf",    "Inter-Regular.ttf"),
    ("segoeuib.ttf",   "Inter-Bold.ttf"),
    ("segoeuii.ttf",   "Inter-Italic.ttf"),
    ("segoeuil.ttf",   "Inter-Thin.ttf"),
    ("segoeuisl.ttf",  "Inter-Light.ttf"),
    ("segoeuiz.ttf",   "Inter-BoldItalic.ttf"),
    ("seguibl.ttf",    "Inter-Black.ttf"),
    ("seguibli.ttf",   "Inter-BlackItalic.ttf"),
    ("seguili.ttf",    "Inter-ThinItalic.ttf"),
    ("seguisb.ttf",    "Inter-SemiBold.ttf"),
    ("seguisbi.ttf",   "Inter-SemiBoldItalic.ttf"),
    ("seguisli.ttf",   "Inter-LightItalic.ttf"),
]

# 紧凑间距映射表
SEGOE_MAPPING_COMPACT = [
    ("segoeui.ttf",    "InterDisplay-Regular.ttf"),
    ("segoeuib.ttf",   "InterDisplay-Bold.ttf"),
    ("segoeuii.ttf",   "InterDisplay-Italic.ttf"),
    ("segoeuil.ttf",   "InterDisplay-Thin.ttf"),
    ("segoeuisl.ttf",  "InterDisplay-Light.ttf"),
    ("segoeuiz.ttf",   "InterDisplay-BoldItalic.ttf"),
    ("seguibl.ttf",    "InterDisplay-Black.ttf"),
    ("seguibli.ttf",   "InterDisplay-BlackItalic.ttf"),
    ("seguili.ttf",    "InterDisplay-ThinItalic.ttf"),
    ("seguisb.ttf",    "InterDisplay-SemiBold.ttf"),
    ("seguisbi.ttf",   "InterDisplay-SemiBoldItalic.ttf"),
    ("seguisli.ttf",   "InterDisplay-LightItalic.ttf"),
]

def get_segoe_mapping():
    # 支持 custom 模式
    if config.get('FONT_PACKAGE_SOURCE', 'local') == 'custom':
        mapping = config.get('segoe_mapping', [])
        if isinstance(mapping, dict):
            return list(mapping.items())
        return [tuple(x) for x in mapping]
    style = config.get('SEGOE_UI_SPACING_STYLE', 'loose').lower()
    if style == 'compact':
        return SEGOE_MAPPING_COMPACT
    return SEGOE_MAPPING_LOOSE


def copy_font_info(dst, info_json):
    font = TTFont(dst)
    name_table = font['name']
    name_table.names.clear()
    for field in info_json.get('name_fields', []):
        parts = dict(item.strip().split('=', 1) for item in field.split(',') if '=' in item)
        rec = NameRecord()
        rec.nameID = int(parts.get('NameID', 0))
        rec.platformID = int(parts.get('Platform', 3))
        rec.platEncID = int(parts.get('Encoding', 1))
        rec.langID = int(parts.get('Lang', 0))
        rec.string = parts.get('Value', '').encode('utf-16-be')
        name_table.names.append(rec)
    font.save(dst)


def batch_rename_and_patch():
    font_info_path = os.path.join(FONT_INFO_DIR, 'segoe_font_info.json')
    with open(font_info_path, 'r', encoding='utf-8') as f:
        infos = json.load(f)
    info_map = {info['file'].lower(): info for info in infos}
    mapping = get_segoe_mapping()
    temp_dir = config.get('TEMP_DIR', './temp')
    for segoe_name, inter_name in mapping:
        try:
            rel_inter_path = find_font_file(temp_dir, inter_name)
            inter_path = os.path.join(temp_dir, rel_inter_path)
            segoe_out = os.path.join(DST_DIR, segoe_name)
            safe_copy(inter_path, segoe_out)
            info = info_map.get(segoe_name.lower())
            if info:
                copy_font_info(segoe_out, info)
        except Exception as e:
            print(f"[WARN] 找不到源字体: {inter_name}，查找异常: {e}")


if __name__ == '__main__':
    batch_rename_and_patch()