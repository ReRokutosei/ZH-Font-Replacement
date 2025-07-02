import json
import os
import shutil

import yaml
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._n_a_m_e import NameRecord

config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
with open(config_path, encoding='utf-8') as f:
    config = yaml.safe_load(f)

if not isinstance(config, dict):
    raise RuntimeError(f"config.yaml 解析异常，返回类型: {type(config)}, 内容: {config}")
REF_DIR = os.path.join(config.get('TEMP_DIR', './temp'), 'extras', 'ttf')  # 直接使用解压后的单独ttf目录
DST_DIR = config.get('TEMP_DIR', './temp')
FONT_INFO_DIR = './font_info'

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
    for segoe_name, inter_name in SEGOE_MAPPING_LOOSE:
        inter_path = os.path.join(REF_DIR, inter_name)
        segoe_out = os.path.join(DST_DIR, segoe_name)
        if os.path.exists(inter_path):
            shutil.copy(inter_path, segoe_out)
            info = info_map.get(segoe_name.lower())
            if info:
                copy_font_info(segoe_out, info)
        else:
            print(f"[WARN] 找不到源字体: {inter_path}")


if __name__ == '__main__':
    batch_rename_and_patch()