import json
import logging
import os
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

import yaml
from fontTools.ttLib import TTCollection, TTFont

from utils.file_ops import find_font_file, safe_copy
from utils.progress import print_progress_bar

config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
with open(config_path, encoding="utf-8") as f:
    config = yaml.safe_load(f)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# 等宽映射表
MSYH_MAPPING_MONOSPACED = [
    ("msyh0.ttf", "SarasaGothicSC-Regular.ttf"),
    ("msyh1.ttf", "SarasaUiSC-Regular.ttf"),
    ("msyh2.ttf", "SarasaGothicSC-Italic.ttf"),
    ("msyh3.ttf", "SarasaUiSC-Italic.ttf"),
    ("msyhbd0.ttf", "SarasaGothicSC-Bold.ttf"),
    ("msyhbd1.ttf", "SarasaUiSC-Bold.ttf"),
    ("msyhbd2.ttf", "SarasaGothicSC-BoldItalic.ttf"),
    ("msyhbd3.ttf", "SarasaUiSC-BoldItalic.ttf"),
    ("msyhl0.ttf", "SarasaGothicSC-Light.ttf"),
    ("msyhl1.ttf", "SarasaUiSC-Light.ttf"),
    ("msyhl2.ttf", "SarasaGothicSC-LightItalic.ttf"),
    ("msyhl3.ttf", "SarasaUiSC-LightItalic.ttf"),
    ("msyhsb0.ttf", "SarasaGothicSC-SemiBold.ttf"),
    ("msyhsb1.ttf", "SarasaUiSC-SemiBold.ttf"),
    ("msyhsb2.ttf", "SarasaGothicSC-SemiBoldItalic.ttf"),
    ("msyhsb3.ttf", "SarasaUiSC-SemiBoldItalic.ttf"),
    ("msyhxl0.ttf", "SarasaGothicSC-ExtraLight.ttf"),
    ("msyhxl1.ttf", "SarasaUiSC-ExtraLight.ttf"),
    ("msyhxl2.ttf", "SarasaGothicSC-ExtraLightItalic.ttf"),
    ("msyhxl3.ttf", "SarasaUiSC-ExtraLightItalic.ttf"),
]

# 不等宽映射表（proportional）
MSYH_MAPPING_PROPORTIONAL = [
    ("msyh0.ttf", "SarasaGothicSC-Regular.ttf"),
    ("msyh1.ttf", "SarasaGothicSC-Regular.ttf"),
    ("msyh2.ttf", "SarasaGothicSC-Italic.ttf"),
    ("msyh3.ttf", "SarasaGothicSC-Italic.ttf"),
    ("msyhbd0.ttf", "SarasaGothicSC-Bold.ttf"),
    ("msyhbd1.ttf", "SarasaGothicSC-Bold.ttf"),
    ("msyhbd2.ttf", "SarasaGothicSC-BoldItalic.ttf"),
    ("msyhbd3.ttf", "SarasaGothicSC-BoldItalic.ttf"),
    ("msyhl0.ttf", "SarasaGothicSC-Light.ttf"),
    ("msyhl1.ttf", "SarasaGothicSC-Light.ttf"),
    ("msyhl2.ttf", "SarasaGothicSC-LightItalic.ttf"),
    ("msyhl3.ttf", "SarasaGothicSC-LightItalic.ttf"),
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
    "msyh.ttc": ["msyh0.ttf", "msyh1.ttf", "msyh2.ttf", "msyh3.ttf"],
    "msyhbd.ttc": ["msyhbd0.ttf", "msyhbd1.ttf", "msyhbd2.ttf", "msyhbd3.ttf"],
    "msyhl.ttc": ["msyhl0.ttf", "msyhl1.ttf", "msyhl2.ttf", "msyhl3.ttf"],
    "msyhsb.ttc": ["msyhsb0.ttf", "msyhsb1.ttf", "msyhsb2.ttf", "msyhsb3.ttf"],
    "msyhxl.ttc": ["msyhxl0.ttf", "msyhxl1.ttf", "msyhxl2.ttf", "msyhxl3.ttf"],
}


def load_font_info():
    with open("./font_info/msyh_font_info.json", "r", encoding="utf-8") as f:
        infos = json.load(f)
    return {(info["file"].lower(), info.get("index", 0)): info for info in infos}


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

    name = re.sub(r"[^A-Za-z0-9_-]", "", name)
    return name[:63]


def set_names_with_json(ttf_path, file_name):
    ttc, index = parse_ttf_filename(file_name)

    if not ttc or index is None:
        logging.warning(f"无法解析 {file_name} 的 ttc 组和 index，跳过 name 字段设置")
        return
    key = (ttc.lower(), index)
    info = font_info_map.get(key)
    if not info:
        logging.warning(f"未找到 {ttc} index={index} 的元信息，跳过 name 字段设置")
        return
    font = TTFont(ttf_path)
    name_table = font["name"]
    if not hasattr(name_table, "setName"):

        logging.error(
            f"font['name'] 没有 setName 方法，无法设置 name 字段。请检查 fontTools 版本或字体文件: {ttf_path}"
        )
        return
    for field in info.get("name_fields", []):
        parts = dict(
            item.strip().split("=", 1) for item in field.split(",") if "=" in item
        )
        nameID = int(parts.get("NameID", 0))
        platformID = int(parts.get("Platform", 3))
        platEncID = int(parts.get("Encoding", 1))
        langID = int(parts.get("Lang", 0))
        value = parts.get("Value", "")
        # 修正 PostScript Name（nameID=6）
        if nameID == 6:
            value = fix_postscript_name(value)
        try:
            name_table.setName(value, nameID, platformID, platEncID, langID)
        except Exception as e:
            logging.warning(f"setName failed: {e}")
    font.save(ttf_path)


def get_msyh_mapping():
    # 支持 custom 模式
    if config.get("FONT_PACKAGE_SOURCE", "local") == "custom":
        mapping = config.get("msyh_mapping", [])
        # 允许为 dict 或 list，自动转为 (dst, src) 列表
        if isinstance(mapping, dict):
            return list(mapping.items())
        return [tuple(x) for x in mapping]
    style = config.get("MS_YAHEI_NUMERALS_STYLE", "monospaced").lower()
    if style == "proportional":
        return MSYH_MAPPING_PROPORTIONAL
    return MSYH_MAPPING_MONOSPACED


def batch_copy_msyh_ttf():
    mapping = get_msyh_mapping()
    temp_dir = config["TEMP_DIR"]
    total = len(mapping)
    logging.info(f"开始复制源TTF文件，共 {total} 个文件")

    copied_count = 0
    failed_count = 0

    for idx, (dst, src) in enumerate(mapping, 1):
        try:
            rel_src_path = find_font_file(temp_dir, src)
            src_path = os.path.join(temp_dir, rel_src_path)
            dst_path = os.path.join(temp_dir, dst)
            safe_copy(src_path, dst_path)
            copied_count += 1
            print_progress_bar(idx, total, prefix="复制源TTF文件", suffix=f"{dst} ({idx}/{total})")
            logging.debug(f"复制成功: {src} -> {dst}")
        except Exception as e:
            failed_count += 1
            print()
            logging.warning(f"源字体不存在: {src}，查找异常: {e}")
    
    print()  # 进度条完成后换行
    logging.info(f"TTF文件复制完成 - 成功: {copied_count}, 失败: {failed_count}")

    if failed_count > 0:
        logging.warning(f"有 {failed_count} 个源TTF文件复制失败")


def batch_patch_names():
    mapping = get_msyh_mapping()
    total = len(mapping)
    logging.info(f"开始设置字体Name信息，共 {total} 个文件")

    processed_count = 0
    skipped_count = 0

    for idx, (dst, _) in enumerate(mapping, 1):
        try:
            ttf_path = os.path.join(config["TEMP_DIR"], dst)
            set_names_with_json(ttf_path, dst)
            processed_count += 1
            print_progress_bar(idx, total, prefix="设置字体Name信息", suffix=f"{dst} ({idx}/{total})")
        except Exception as e:
            skipped_count += 1
            logging.warning(f"设置字体Name信息失败: {dst}, 错误: {e}")
    
    print()  # 进度条完成后换行
    logging.info(f"字体Name信息设置完成 - 处理: {processed_count}, 跳过: {skipped_count}")


def generate_ttc_with_fonttools(ttf_list, ttc_path):
    """
    用 FontTools 合并 ttf_list 为 ttc_path，兼容新版和旧版 fontTools
    优化版本：减少内存使用，提升合并速度
    """
    # 优化1: 使用 lazy=True 延迟加载，减少初始内存占用
    fonts = []
    try:
        # 优化2: 批量加载字体，减少重复的 I/O 操作
        for ttf in ttf_list:
            # 使用 lazy=True 延迟加载表数据，只加载必要的表
            font = TTFont(ttf, lazy=True, recalcBBoxes=False, recalcTimestamp=False)
            fonts.append(font)

        # 优化3: 创建 TTC 时使用更高效的方式
        try:
            ttc = TTCollection(fonts)
        except TypeError:
            # 兼容旧版 fontTools
            ttc = TTCollection()
            ttc.fonts = fonts

        # 优化4: 直接保存，避免额外的内存复制
        ttc.save(ttc_path)

    finally:
        # 优化5: 及时清理内存
        for font in fonts:
            try:
                font.close()
            except:
                pass
        del fonts


def batch_generate_ttc(ttc_names=None, use_parallel=None, max_workers=None):
    """
    ttc_names: 指定只生成哪些 ttc（如 ["msyh.ttc"]），为 None 时全量生成
    use_parallel: 是否使用并行处理，为 None 时从配置文件读取
    max_workers: 最大工作线程数，为 None 时使用默认值
    """
    # 从配置文件读取并行处理设置
    if use_parallel is None:
        use_parallel = config.get("ENABLE_PARALLEL_TTC_GENERATION", True)
    if max_workers is None:
        max_workers = config.get("MAX_PARALLEL_TTC_WORKERS", None)

    if ttc_names is None:
        ttc_names = list(TTC_GROUPS.keys())

    # 预先检查所有文件是否存在，避免重复检查
    ttc_tasks = []
    for ttc_name in ttc_names:
        ttf_list = TTC_GROUPS[ttc_name]
        ttf_paths = [
            os.path.abspath(os.path.join(config["TEMP_DIR"], ttf)) for ttf in ttf_list
        ]
        ttf_paths_exist = [p for p in ttf_paths if os.path.exists(p)]

        if len(ttf_paths_exist) != 4:
            logging.warning(
                f"生成 {ttc_name} 时有缺失: {ttf_paths_exist}，应有: {ttf_paths}"
            )
            continue

        ttc_path = os.path.abspath(os.path.join(config["TEMP_DIR"], ttc_name))
        ttc_tasks.append((ttc_name, ttf_paths_exist, ttc_path))

    if not ttc_tasks:
        logging.warning("没有找到需要生成的 TTC 文件")
        return

    # 根据配置决定是否使用并行处理
    if use_parallel:
        if max_workers is None:
            # 对于5个TTC文件，使用3-4个工作线程比较合适
            max_workers = min(4, len(ttc_tasks))

        logging.info(
            f"使用并行处理生成 [{len(ttc_tasks)}/{len(TTC_GROUPS)}] 个 TTC 文件，工作线程数: {max_workers}"
        )
        success_count, failed_count = _batch_generate_ttc_parallel(ttc_tasks, max_workers)
    else:
        logging.info(
            f"使用串行处理生成 [{len(ttc_tasks)}/{len(TTC_GROUPS)}] 个 TTC 文件"
        )
        success_count, failed_count = _batch_generate_ttc_serial(ttc_tasks)

    logging.info(f"TTC 生成完成 - 成功: {success_count}, 失败: {failed_count}")


def _generate_single_ttc(ttc_name, ttf_paths, ttc_path):
    """
    生成单个 TTC 文件的辅助函数，用于并行处理
    返回 (ttc_name, success, duration, error_msg)
    """
    start_time = time.time()
    try:
        generate_ttc_with_fonttools(ttf_paths, ttc_path)
        duration = time.time() - start_time
        return (ttc_name, True, duration, "")
    except Exception as e:
        duration = time.time() - start_time
        error_msg = f"{e}\n{traceback.format_exc()}"
        return (ttc_name, False, duration, error_msg)


def _batch_generate_ttc_parallel(ttc_tasks, max_workers):
    """并行生成TTC文件"""
    total = len(ttc_tasks)
    success_count = 0
    failed_count = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for ttc_name, ttf_paths, ttc_path in ttc_tasks:
            future = executor.submit(_generate_single_ttc, ttc_name, ttf_paths, ttc_path)
            futures.append((ttc_name, future))
        
        for idx, (ttc_name, future) in enumerate(futures, 1):
            try:
                success = future.result()
                if success:
                    success_count += 1
                else:
                    failed_count += 1
                print_progress_bar(idx, total, prefix="生成TTC文件", suffix=f"{ttc_name} ({idx}/{total})")
            except Exception as e:
                failed_count += 1
                logging.error(f"生成 {ttc_name} 失败: {e}")
        
        print()  # 进度条完成后换行
    return success_count, failed_count


def _batch_generate_ttc_serial(ttc_tasks):
    """串行生成TTC文件"""
    total = len(ttc_tasks)
    success_count = 0
    failed_count = 0
    
    for idx, (ttc_name, ttf_paths, ttc_path) in enumerate(ttc_tasks, 1):
        try:
            if _generate_single_ttc(ttc_name, ttf_paths, ttc_path):
                success_count += 1
            else:
                failed_count += 1
            print_progress_bar(idx, total, prefix="生成TTC文件", suffix=f"{ttc_name} ({idx}/{total})")
        except Exception as e:
            failed_count += 1
            logging.error(f"生成 {ttc_name} 失败: {e}")
    
    print()  # 进度条完成后换行
    return success_count, failed_count


def copy_individual_ttf_to_result(result_dir):
    """复制单独的TTF文件到结果目录"""
    if not config.get("INCLUDE_INDIVIDUAL_TTF", True):
        return

    mapping = get_msyh_mapping()
    total = len(mapping)
    logging.info("开始复制单独的TTF文件到结果目录...")
    
    copied_count = 0
    for idx, (dst, _) in enumerate(mapping, 1):
        try:
            src = os.path.join(config["TEMP_DIR"], dst)
            dst_path = os.path.join(result_dir, dst)
            safe_copy(src, dst_path)
            copied_count += 1
            print_progress_bar(idx, total, prefix="复制TTF到结果目录", suffix=f"{dst} ({idx}/{total})")
        except Exception as e:
            logging.error(f"复制 {dst} 到结果目录失败: {e}")
    
    print()  # 进度条完成后换行
    logging.info(f"TTF文件复制完成，共复制 {copied_count} 个文件到结果目录")


def check_ttc_generated():
    temp_dir = config.get("TEMP_DIR", "./temp")
    ttc_files = ["msyh.ttc", "msyhbd.ttc", "msyhl.ttc", "msyhxl.ttc", "msyhsb.ttc"]
    return all(os.path.exists(os.path.join(temp_dir, f)) for f in ttc_files)


def copy_result_files(result_dir):
    """复制生成的字体文件到结果目录"""
    # 复制TTC文件
    ttc_files = list(TTC_GROUPS.keys())
    total_ttc = len(ttc_files)
    
    for idx, ttc_name in enumerate(ttc_files, 1):
        src = os.path.join(config["TEMP_DIR"], ttc_name)
        dst = os.path.join(result_dir, ttc_name)
        try:
            safe_copy(src, dst)
            print_progress_bar(idx, total_ttc, prefix="复制TTC到结果目录", suffix=f"{ttc_name} ({idx}/{total_ttc})")
        except Exception as e:
            logging.error(f"复制 {ttc_name} 到结果目录失败: {e}")
    
    print()  # 进度条完成后换行
    
    # 复制单独的TTF文件（如果配置允许）
    copy_individual_ttf_to_result(result_dir)


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
