import auto_configs as conf
import fetch_original as fetch
import copy_result as copy
import logging
import sys
import os
import subprocess

FFPYTHON_PATH = r"D:\Develop\FontForgeBuilds\bin\ffpython.exe"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def validate_config():
    """验证配置的有效性"""
    if not any([conf.ENABLE_MS_YAHEI, conf.ENABLE_SIMSUN, 
                conf.ENABLE_SIMSUN_EXT, conf.ENABLE_HANSCODE]):
        logging.error("错误：至少需要启用一项生成功能")
        sys.exit(1)

def create_directories():
    """创建必要的目录"""
    fetch.clear_dir(conf.TEMP_DIR)
    fetch.clear_dir(conf.RESULT_DIR)
    if not os.path.exists(conf.SOURCE_FILES_DIR):
        os.makedirs(conf.SOURCE_FILES_DIR)

def run_with_ffpython(script, func):
    result = subprocess.run([FFPYTHON_PATH, script, func])
    if result.returncode != 0:
        raise RuntimeError(f"{script} {func} 执行失败")

if __name__ == '__main__':
    try:
        logging.info("开始字体生成流程")
        
        # 验证配置
        validate_config()
        
        # 创建目录
        create_directories()
        
        # 获取所有源文件包
        if conf.DOWNLOAD_MODE == 'local':
            packages = fetch.find_all_local_packages()
            if not packages:
                logging.error("未找到任何本地源文件包，请检查 source_files 目录")
                sys.exit(1)
            for pkg in packages:
                logging.info(f"本地包: {pkg}")
                fetch.unzip(pkg)
        else:
            urls = fetch.get_all_latest()
            if not urls:
                logging.error("未找到任何可用的在线源文件包")
                sys.exit(1)
            for url in urls:
                logging.info(f"下载包: {url}")
                path = fetch.download(url)
                fetch.unzip(path)
        
        # 生成微软雅黑字体
        if conf.ENABLE_MS_YAHEI:
            logging.info("开始生成微软雅黑字体")
            run_with_ffpython("generate_fonts.py", "gen_regular")
            run_with_ffpython("generate_fonts.py", "gen_bold")
            run_with_ffpython("generate_fonts.py", "gen_light")
            run_with_ffpython("generate_fonts.py", "gen_extralight")
            run_with_ffpython("generate_fonts.py", "gen_semibold")
            logging.info("微软雅黑字体生成完成")
        
        # 生成宋体
        if conf.ENABLE_SIMSUN:
            logging.info("开始生成宋体")
            run_with_ffpython("generate_simsun.py", "gen_simsun_ttc")
            logging.info("宋体生成完成")
        
        # 生成宋体扩展
        if conf.ENABLE_SIMSUN_EXT:
            logging.info("开始生成宋体扩展")
            run_with_ffpython("generate_simsun.py", "gen_simsun_ext")
            logging.info("宋体扩展生成完成")
        
        # 复制结果
        copy.copy_result()
        
        logging.info("所有字体生成完成")
        
    except Exception as e:
        logging.error(f"程序执行出错: {str(e)}")
        sys.exit(1)
