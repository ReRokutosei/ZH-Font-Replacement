"""
字体转换相关工具函数
主要包含OTF到TTF的转换功能
"""

import logging
import os
import time
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed

from otf2ttf.official.otf2ttf import (
    otf_to_ttf as official_otf2ttf,
    update_hmtx,
    TTFont,
    MAX_ERR
)

from .config import get_config_value
from .file_ops import ensure_dir_exists
from .progress import print_progress_bar


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


def _convert_otf_to_ttf_worker(otf_path):
    """
    在子进程中运行的OTF转TTF转换函数。
    返回 (otf_path, success: bool, duration: float, error_msg: str)
    """
    start = time.time()
    try:
        # 直接调用官方FontTools的otf2ttf实现
        font = TTFont(otf_path)
        official_otf2ttf(font, max_err=MAX_ERR)
        # 更新hmtx表
        update_hmtx(font, font["glyf"])
        ttf_path = os.path.splitext(otf_path)[0] + '.ttf'
        font.save(ttf_path)
        
        # 清理内存
        del font
        
        success = True
        error_msg = ""
    except Exception as e:
        success = False
        error_msg = str(e)
    end = time.time()
    
    # 只返回必要的信息，减少数据传输
    return (os.path.basename(otf_path), success, end - start, error_msg)


def convert_otf_to_ttf(otf_path, verbose=False):
    """
    使用官方实现将单个 OTF 文件转为 TTF。
    返回 (success: bool, duration: float)
    """
    start = time.time()
    try:
        # 直接调用官方FontTools的otf2ttf实现
        if verbose:
            logging.info(f"[OTF2TTF] 开始转换: {os.path.basename(otf_path)}")
        font = TTFont(otf_path)
        official_otf2ttf(font, max_err=MAX_ERR)
        # 更新hmtx表
        update_hmtx(font, font["glyf"])
        ttf_path = os.path.splitext(otf_path)[0] + '.ttf'
        font.save(ttf_path)
        if verbose:
            logging.info(f"[OTF2TTF] 转换完成: {os.path.basename(ttf_path)}")
        success = True
    except Exception as e:
        if verbose:
            logging.error(f"转换失败: {otf_path} 异常: {str(e)}")
        success = False
    end = time.time()
    return success, end - start


def _classify_font_files_by_mapping(otf_files, msyh_mapping=None, segoe_mapping=None):
    """
    根据映射配置将字体文件分类为中文字体和英文字体。
    返回 (chinese_fonts, english_fonts)
    """
    chinese_fonts = []
    english_fonts = []
    
    # 如果没有映射配置，所有字体都归类为中文字体（默认更保守的处理方式）
    if not msyh_mapping and not segoe_mapping:
        return otf_files, []
    
    # 构建映射文件集合
    msyh_files = set()
    segoe_files = set()
    if msyh_mapping:
        msyh_files = {os.path.basename(src) for _, src in msyh_mapping}
    if segoe_mapping:
        segoe_files = {os.path.basename(src) for _, src in segoe_mapping}
    
    # 分类文件
    for otf_file in otf_files:
        basename = os.path.basename(otf_file)
        if basename in msyh_files:
            chinese_fonts.append(otf_file)
        elif basename in segoe_files:
            english_fonts.append(otf_file)
        else:
            # 未知字体归类为中文字体（更保守的处理方式）
            chinese_fonts.append(otf_file)
    
    return chinese_fonts, english_fonts


def _batch_convert_otf_to_ttf_serial(otf_files, verbose=True):
    """
    串行批量转换 OTF 文件为 TTF。
    """
    ttf_files = []
    global_start = time.time()
    for idx, otf_file in enumerate(otf_files, 1):
        if verbose:
            logging.info(f"[{idx}/{len(otf_files)}] 正在转换: {os.path.basename(otf_file)}")
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


def _batch_convert_otf_to_ttf_parallel(otf_files, verbose=True, max_workers=None, msyh_mapping=None, segoe_mapping=None):
    """
    并行批量转换 OTF 文件为 TTF，支持任务分组和内存优化。
    """
    if max_workers is None:
        max_workers = min(mp.cpu_count(), len(otf_files))
    
    # 分类字体文件
    chinese_fonts, english_fonts = _classify_font_files_by_mapping(otf_files, msyh_mapping, segoe_mapping)
    
    if verbose:
        logging.info(f"字体分类: 中文字体 {len(chinese_fonts)} 个，英文字体 {len(english_fonts)} 个")
    
    ttf_files = []
    global_start = time.time()
    completed_count = 0
    failed_count = 0
    
    # 分组处理：先处理英文字体（通常更快），再处理中文字体
    font_groups = []
    if english_fonts:
        font_groups.append(("英文字体", english_fonts))
    if chinese_fonts:
        font_groups.append(("中文字体", chinese_fonts))
    
    for group_name, group_files in font_groups:
        if verbose:
            logging.info(f"开始处理{group_name}组 ({len(group_files)} 个文件)")
        
        group_start = time.time()
        
        # 为每个组分配工作进程数，中文字体组使用更多进程
        if "中文" in group_name:
            group_workers = min(max_workers, len(group_files))
        else:
            # 英文字体组使用较少进程，避免过度并行
            group_workers = min(max_workers // 2, len(group_files))
        
        if verbose:
            logging.info(f"{group_name}组使用 {group_workers} 个工作进程")
        
        # 使用进程池执行并行转换
        with ProcessPoolExecutor(max_workers=group_workers) as executor:
            # 提交当前组的所有任务
            future_to_otf = {executor.submit(_convert_otf_to_ttf_worker, otf_file): otf_file 
                            for otf_file in group_files}
            
            # 处理完成的任务
            for future in as_completed(future_to_otf):
                otf_file = future_to_otf[future]
                try:
                    filename, success, duration, error_msg = future.result()
                    completed_count += 1
                    
                    if verbose:
                        logging.info(f"[{completed_count}/{len(otf_files)}] 转换完成: {filename} (用时 {duration:.2f} 秒)")
                    
                    if success:
                        ttf_path = os.path.splitext(otf_file)[0] + '.ttf'
                        if os.path.exists(ttf_path):
                            ttf_files.append(ttf_path)
                            if verbose:
                                logging.info(f"✓ 成功: {os.path.basename(ttf_path)}")
                        else:
                            if verbose:
                                logging.error(f"✗ 文件未生成: {os.path.basename(ttf_path)}")
                            failed_count += 1
                    else:
                        if verbose:
                            logging.error(f"✗ 转换失败: {filename} - {error_msg}")
                        failed_count += 1
                        
                except Exception as e:
                    completed_count += 1
                    failed_count += 1
                    if verbose:
                        logging.error(f"✗ 处理异常: {os.path.basename(otf_file)} - {str(e)}")
                
                # 清理已完成的任务引用，释放内存
                del future_to_otf[future]
        
        group_end = time.time()
        if verbose:
            logging.info(f"{group_name}组处理完成，用时 {group_end - group_start:.2f} 秒")
    
    global_end = time.time()
    if verbose:
        success_count = len(ttf_files)
        logging.info(f"并行转换完成: 成功 {success_count}/{len(otf_files)} 个文件，失败 {failed_count} 个")
        logging.info(f"总用时 {global_end - global_start:.2f} 秒")
    
    return ttf_files


def batch_convert_otf_to_ttf(root_dir, verbose=True, target_files=None, use_parallel=True, max_workers=None, msyh_mapping=None, segoe_mapping=None):
    """
    批量转换 OTF 文件为 TTF，支持并行处理。
    root_dir: 根目录
    verbose: 是否详细输出
    target_files: 指定要转换的文件列表（绝对路径），为 None 时转换目录下所有 OTF 文件
    use_parallel: 是否使用并行处理
    max_workers: 最大工作进程数，为 None 时使用 CPU 核心数
    msyh_mapping: 微软雅黑映射，用于字体分类
    segoe_mapping: Segoe UI映射，用于字体分类
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
    
    # 决定是否使用并行处理
    if use_parallel and total > 1:
        # 使用并行处理
        if max_workers is None:
            max_workers = min(mp.cpu_count(), total)
        
        if verbose:
            logging.info(f"使用并行处理，工作进程数: {max_workers}")
        
        return _batch_convert_otf_to_ttf_parallel(otf_files, verbose, max_workers, msyh_mapping, segoe_mapping)
    else:
        # 使用串行处理
        if verbose and total > 1:
            logging.info("使用串行处理")
        return _batch_convert_otf_to_ttf_serial(otf_files, verbose)


def update_mapping_otf_to_ttf(mapping, temp_dir, verbose=True, config=None, msyh_mapping=None, segoe_mapping=None):
    """
    更新映射表中的OTF文件为TTF文件。
    mapping: 原始映射表
    temp_dir: 临时目录
    verbose: 是否详细输出
    config: 配置字典，用于获取并行处理参数
    msyh_mapping: 微软雅黑映射，用于字体分类
    segoe_mapping: Segoe UI映射，用于字体分类
    返回更新后的映射表。
    """
    if not mapping:
        return mapping
    
    # 收集所有需要转换的OTF文件
    items = mapping if isinstance(mapping, list) else mapping.items()
    otf_set = set()
    for dst, src in items:
        if src.lower().endswith('.otf'):
            otf_set.add(os.path.join(temp_dir, src))
    
    # 使用批量转换函数处理所有 OTF 文件
    if otf_set:
        if verbose:
            logging.info(f"发现 {len(otf_set)} 个 OTF 文件需要转换")
        
        # 获取并行处理配置
        use_parallel = True
        max_workers = None
        enable_grouping = True
        if config:
            use_parallel = get_config_value(config, 'ENABLE_PARALLEL_OTF_CONVERSION', True)
            max_workers = get_config_value(config, 'MAX_PARALLEL_WORKERS', None)
            enable_grouping = get_config_value(config, 'ENABLE_FONT_GROUPING', True)
        
        try:
            batch_convert_otf_to_ttf(
                temp_dir, 
                verbose=verbose, 
                target_files=list(otf_set),
                use_parallel=use_parallel,
                max_workers=max_workers,
                msyh_mapping=msyh_mapping if enable_grouping else None,
                segoe_mapping=segoe_mapping if enable_grouping else None
            )
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


def process_custom_font_packages(config):
    """
    处理自定义字体包中的OTF转TTF逻辑
    """
    temp_dir = config.get('TEMP_DIR', './temp')
    if 'msyh_mapping' in config:
        config['msyh_mapping'] = update_mapping_otf_to_ttf(
            config['msyh_mapping'], 
            temp_dir, 
            verbose=True, 
            config=config,
            msyh_mapping=config.get('msyh_mapping'),
            segoe_mapping=config.get('segoe_mapping')
        )
    if 'segoe_mapping' in config:
        config['segoe_mapping'] = update_mapping_otf_to_ttf(
            config['segoe_mapping'], 
            temp_dir, 
            verbose=True, 
            config=config,
            msyh_mapping=config.get('msyh_mapping'),
            segoe_mapping=config.get('segoe_mapping')
        )
