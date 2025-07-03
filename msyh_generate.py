import json
import os
import shutil as fs
import sys

import yaml
from fontTools.ttLib import TTCollection, TTFont, newTable
from fontTools.ttLib.tables._n_a_m_e import NameRecord

from project_utils import find_font_file

config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
with open(config_path, encoding='utf-8') as f:
    config = yaml.safe_load(f)


# 等宽映射表
MSYH_MAPPING_MONOSPACED = [
    ("msyh0.ttf",   "SarasaGothicSC-Regular.ttf"),
    ("msyh1.ttf",   "SarasaUiSC-Regular.ttf"),
    ("msyh2.ttf",   "SarasaUiSC-Italic.ttf"),
    ("msyh3.ttf",   "SarasaGothicSC-Italic.ttf"),
    ("msyhbd0.ttf", "SarasaUiSC-Bold.ttf"),
    ("msyhbd1.ttf", "SarasaGothicSC-Bold.ttf"),
    ("msyhbd2.ttf", "SarasaUiSC-BoldItalic.ttf"),
    ("msyhbd3.ttf", "SarasaGothicSC-BoldItalic.ttf"),
    ("msyhl0.ttf",  "SarasaUiSC-Light.ttf"),
    ("msyhl1.ttf",  "SarasaGothicSC-Light.ttf"),
    ("msyhl2.ttf",  "SarasaUiSC-LightItalic.ttf"),
    ("msyhl3.ttf",  "SarasaGothicSC-LightItalic.ttf"),
    ("msyhsb0.ttf", "SarasaUiSC-SemiBold.ttf"),
    ("msyhsb1.ttf", "SarasaGothicSC-SemiBold.ttf"),
    ("msyhsb2.ttf", "SarasaUiSC-SemiBoldItalic.ttf"),
    ("msyhsb3.ttf", "SarasaGothicSC-SemiBoldItalic.ttf"),
    ("msyhxl0.ttf", "SarasaUiSC-ExtraLight.ttf"),
    ("msyhxl1.ttf", "SarasaGothicSC-ExtraLight.ttf"),
    ("msyhxl2.ttf", "SarasaUiSC-ExtraLightItalic.ttf"),
    ("msyhxl3.ttf", "SarasaGothicSC-ExtraLightItalic.ttf"),
]

# 不等宽映射表（proportional）
MSYH_MAPPING_PROPORTIONAL = [
    ("msyh0.ttf",   "SarasaGothicSC-Regular.ttf"),
    ("msyh1.ttf",   "SarasaGothicSC-Regular.ttf"),
    ("msyh2.ttf",   "SarasaGothicSC-Italic.ttf"),
    ("msyh3.ttf",   "SarasaGothicSC-Italic.ttf"),
    ("msyhbd0.ttf", "SarasaGothicSC-Bold.ttf"),
    ("msyhbd1.ttf", "SarasaGothicSC-Bold.ttf"),
    ("msyhbd2.ttf", "SarasaGothicSC-BoldItalic.ttf"),
    ("msyhbd3.ttf", "SarasaGothicSC-BoldItalic.ttf"),
    ("msyhl0.ttf",  "SarasaGothicSC-Light.ttf"),
    ("msyhl1.ttf",  "SarasaGothicSC-Light.ttf"),
    ("msyhl2.ttf",  "SarasaGothicSC-LightItalic.ttf"),
    ("msyhl3.ttf",  "SarasaGothicSC-LightItalic.ttf"),
    ("msyhsb0.ttf", "SarasaGothicSC-SemiBold.ttf"),
    ("msyhsb1.ttf", "SarasaGothicSC-SemiBold.ttf"),
    ("msyhsb2.ttf", "SarasaGothicSC-SemiBoldItalic.ttf"),
    ("msyhsb3.ttf", "SarasaGothicSC-SemiBoldItalic.ttf"),
    ("msyhxl0.ttf", "SarasaGothicSC-ExtraLight.ttf"),
    ("msyhxl1.ttf", "SarasaGothicSC-ExtraLight.ttf"),
    ("msyhxl2.ttf", "SarasaGothicSC-ExtraLightItalic.ttf"),
    ("msyhxl3.ttf", "SarasaGothicSC-ExtraLightItalic.ttf"),
]

TTC_GROUPS = {
    "msyh.ttc":   ["msyh0.ttf", "msyh1.ttf", "msyh2.ttf", "msyh3.ttf"],
    "msyhbd.ttc": ["msyhbd0.ttf", "msyhbd1.ttf", "msyhbd2.ttf", "msyhbd3.ttf"],
    "msyhl.ttc":  ["msyhl0.ttf", "msyhl1.ttf", "msyhl2.ttf", "msyhl3.ttf"],
    "msyhsb.ttc": ["msyhsb0.ttf", "msyhsb1.ttf", "msyhsb2.ttf", "msyhsb3.ttf"],
    "msyhxl.ttc": ["msyhxl0.ttf", "msyhxl1.ttf", "msyhxl2.ttf", "msyhxl3.ttf"],
}

def load_font_info():
    with open('./font_info/msyh_font_info.json', 'r', encoding='utf-8') as f:
        infos = json.load(f)
    return { (info['file'].lower(), info.get('index', 0)): info for info in infos }

font_info_map = load_font_info()

def parse_ttf_filename(ttf_filename):
    # 解析如 msyh0.ttf, msyhbd2.ttf, msyhl3.ttf, msyhsb1.ttf, msyhxl0.ttf
    import re
    m = re.match(r"(msyh|msyhbd|msyhl|msyhsb|msyhxl)(\d)\.ttf", ttf_filename)
    if m:
        group = m.group(1)
        idx = int(m.group(2))
        if group == "msyh":
            ttc = "msyh.ttc"
        elif group == "msyhbd":
            ttc = "msyhbd.ttc"
        elif group == "msyhl":
            ttc = "msyhl.ttc"
        elif group == "msyhsb":
            ttc = "msyhsb.ttc"
        elif group == "msyhxl":
            ttc = "msyhxl.ttc"
        else:
            ttc = None
        return ttc, idx
    return None, None

def fix_postscript_name(name):
    import re
    name = re.sub(r'[^A-Za-z0-9_-]', '', name)
    return name[:63]

def set_names_with_json(ttf_path, file_name):
    ttc, index = parse_ttf_filename(file_name)
    if not ttc or index is None:
        print(f"[WARN] 无法解析 {file_name} 的 ttc 组和 index，跳过 name 字段设置")
        return
    key = (ttc.lower(), index)
    info = font_info_map.get(key)
    if not info:
        print(f"[WARN] 未找到 {ttc} index={index} 的元信息，跳过 name 字段设置")
        return
    font = TTFont(ttf_path)
    name_table = font["name"]
    if not hasattr(name_table, "setName"):
        print(f"[ERROR] font['name'] 没有 setName 方法，无法设置 name 字段。请检查 fontTools 版本或字体文件: {ttf_path}")
        return
    for field in info.get('name_fields', []):
        parts = dict(item.strip().split('=', 1) for item in field.split(',') if '=' in item)
        nameID = int(parts.get('NameID', 0))
        platformID = int(parts.get('Platform', 3))
        platEncID = int(parts.get('Encoding', 1))
        langID = int(parts.get('Lang', 0))
        value = parts.get('Value', '')
        # 修正 PostScript Name（nameID=6）
        if nameID == 6:
            value = fix_postscript_name(value)
        try:
            name_table.setName(value, nameID, platformID, platEncID, langID)
        except Exception as e:
            print(f"[WARN] setName failed: {e}")
    font.save(ttf_path)


def get_msyh_mapping():
    style = config.get('MS_YAHEI_NUMERALS_STYLE', 'monospaced').lower()
    if style == 'proportional':
        return MSYH_MAPPING_PROPORTIONAL
    return MSYH_MAPPING_MONOSPACED

def batch_copy_msyh_ttf():
    mapping = get_msyh_mapping()
    temp_dir = config['TEMP_DIR']
    for dst, src in mapping:
        try:
            rel_src_path = find_font_file(temp_dir, src)
            src_path = os.path.join(temp_dir, rel_src_path)
            dst_path = os.path.join(temp_dir, dst)
            fs.copy(src_path, dst_path)
        except Exception as e:
            print(f"[WARN] 源字体不存在: {src}，查找异常: {e}")

def batch_patch_names():
    mapping = get_msyh_mapping()
    for dst, _ in mapping:
        dst_path = os.path.join(config['TEMP_DIR'], dst)
        if os.path.exists(dst_path):
            set_names_with_json(dst_path, dst)


def generate_ttc_with_fonttools(ttf_list, ttc_path):
    """
    用 FontTools 合并 ttf_list 为 ttc_path，兼容新版和旧版 fontTools
    """
    from fontTools.ttLib import TTCollection, TTFont
    fonts = [TTFont(ttf, recalcBBoxes=False, recalcTimestamp=False) for ttf in ttf_list]
    try:
        ttc = TTCollection(fonts)
    except TypeError:
        ttc = TTCollection()
        ttc.fonts = fonts
    ttc.save(ttc_path)

def batch_generate_ttc(ttc_names=None):
    """
    ttc_names: 指定只生成哪些 ttc（如 ["msyh.ttc"]），为 None 时全量生成
    """
    if ttc_names is None:
        ttc_names = list(TTC_GROUPS.keys())
    for ttc_name in ttc_names:
        ttf_list = TTC_GROUPS[ttc_name]
        ttf_paths = [os.path.abspath(os.path.join(config['TEMP_DIR'], ttf)) for ttf in ttf_list]
        ttf_paths_exist = [p for p in ttf_paths if os.path.exists(p)]
        if len(ttf_paths_exist) != 4:
            print(f"[WARN] 生成 {ttc_name} 时有缺失: {ttf_paths_exist}")
            continue
        ttc_path = os.path.abspath(os.path.join(config['TEMP_DIR'], ttc_name))
        try:
            generate_ttc_with_fonttools(ttf_paths_exist, ttc_path)
            print(f"[INFO] 生成 {ttc_name} 成功 (FontTools)")
        except Exception as e:
            print(f"[ERROR] 生成 {ttc_name} 失败 (FontTools): {e}")


def check_ttc_generated():
    temp_dir = config.get('TEMP_DIR', './temp')
    ttc_files = ["msyh.ttc", "msyhbd.ttc", "msyhl.ttc", "msyhel.ttc", "msyhsb.ttc"]
    return all(os.path.exists(os.path.join(temp_dir, f)) for f in ttc_files)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "batch_msyh":
            batch_copy_msyh_ttf()
            batch_patch_names()
            batch_generate_ttc()
        elif arg == "gen_regular":
            batch_copy_msyh_ttf()
            batch_patch_names()
            batch_generate_ttc(["msyh.ttc"])
        elif arg == "gen_bold":
            batch_copy_msyh_ttf()
            batch_patch_names()
            batch_generate_ttc(["msyhbd.ttc"])
        elif arg == "gen_light":
            batch_copy_msyh_ttf()
            batch_patch_names()
            batch_generate_ttc(["msyhl.ttc"])
        elif arg == "gen_extralight":
            batch_copy_msyh_ttf()
            batch_patch_names()
            batch_generate_ttc(["msyhxl.ttc"])
        elif arg == "gen_semibold":
            batch_copy_msyh_ttf()
            batch_patch_names()
            batch_generate_ttc(["msyhsb.ttc"])
        else:
            print(f"未知参数: {arg}")
    else:
        batch_copy_msyh_ttf()
        batch_patch_names()
        batch_generate_ttc()
