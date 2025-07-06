import logging

from msyh_generate import batch_copy_msyh_ttf, batch_patch_names, batch_generate_ttc, copy_individual_ttf_to_result, check_ttc_generated, copy_result_files


def generate_ms_yahei(config, result_subdir):
    logging.info("开始生成微软雅黑字体")
    
    # 一次性生成所有TTC文件，而不是分别调用
    # 先复制源TTF文件
    batch_copy_msyh_ttf()
    # 设置字体名称
    batch_patch_names()
    # 生成TTC文件
    batch_generate_ttc()
    
    if check_ttc_generated():
        # 复制TTC文件到结果目录
        copy_result_files(result_subdir)
        # 复制20个覆写元信息的TTF文件（如果配置启用）
        copy_individual_ttf_to_result(result_subdir)
        logging.info("微软雅黑字体生成完成，并已复制到结果目录")
    else:
        logging.error("微软雅黑字体未生成任何文件，请检查流程！")
        raise RuntimeError("微软雅黑字体未生成任何文件，请检查流程！")
