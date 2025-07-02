import logging
import os

import fetch_sarasa as sarasa
from msyh_workflow import generate_ms_yahei
from project_utils import (clean_temp_dir, create_directories,
                           get_new_result_dir, load_config, validate_config)
from segoe_workflow import generate_segoe_ui

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def main():
    config = load_config()
    try:
        logging.info("开始字体生成流程")
        validate_config(config)
        create_directories(config)
        # 获取所有源文件包
        if config.get('ENABLE_MS_YAHEI', True):
            if config.get('DOWNLOAD_MODE', 'local') == 'local':
                packages = sarasa.find_all_local_packages()
                if not packages:
                    logging.error("未找到任何本地源文件包，请检查 source_files 目录")
                    raise SystemExit(1)
                for pkg in packages:
                    logging.info(f"本地包: {pkg}")
                    sarasa.unzip(pkg)
            else:
                urls = sarasa.get_all_latest()
                if not urls:
                    logging.error("未找到任何可用的在线源文件包")
                    raise SystemExit(1)
                for url in urls:
                    path = sarasa.download(url, save_dir=config.get('SOURCE_FILES_DIR', './source_files'))
                    logging.info(f"准备解压: {os.path.basename(path)}")
                    sarasa.unzip(path)
        # 生成唯一结果子目录
        result_subdir = get_new_result_dir(config)
        # 生成微软雅黑字体
        if config.get('ENABLE_MS_YAHEI', True):
            generate_ms_yahei(config, result_subdir)
        # 生成Segoe UI字体
        if config.get('ENABLE_SEGOE_UI', True):
            generate_segoe_ui(config, result_subdir)
        logging.info(f"所有字体生成完成，结果目录：{result_subdir}")
        # 自动清理 temp 目录（可选）
        if config.get('CLEAN_TEMP_ON_SUCCESS', False):
            clean_temp_dir(config)
    except Exception as e:
        logging.error(f"程序执行出错: {str(e)}")
        raise SystemExit(1)

if __name__ == '__main__':
    main()