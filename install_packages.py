import subprocess
import sys
import os
import shutil
import glob
import yaml

def install_normal_packages():
    pkgs = ["fonttools", "requests", "py7zr", "wget", "pyyaml"]
    print("正在为当前Python环境安装依赖:", pkgs)
    subprocess.check_call([sys.executable, "-m", "pip", "install"] + pkgs)

def get_python_site_packages(py_exe):
    # 获取site-packages路径
    code = (
        "import site; print([p for p in site.getsitepackages() if 'site-packages' in p][0])"
    )
    out = subprocess.check_output([py_exe, "-c", code], encoding="utf-8")
    return out.strip()

def copy_pyyaml_to_ffpython():
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path, encoding='utf-8') as f:
        config = yaml.safe_load(f)
    ffpython_path = config.get('FFPYTHON_PATH')
    if not ffpython_path or not os.path.exists(ffpython_path):
        print(f"未找到 FFPYTHON_PATH: {ffpython_path}")
        return
    # 获取当前python和ffpython的site-packages
    py_site = get_python_site_packages(sys.executable)
    ff_site = get_python_site_packages(ffpython_path)
    print(f"当前Python site-packages: {py_site}")
    print(f"ffpython site-packages: {ff_site}")
    # 复制yaml文件夹
    src_yaml = os.path.join(py_site, 'yaml')
    dst_yaml = os.path.join(ff_site, 'yaml')
    if os.path.exists(dst_yaml):
        shutil.rmtree(dst_yaml)
    shutil.copytree(src_yaml, dst_yaml)
    # 复制 _yaml.*.pyd
    for file in glob.glob(os.path.join(py_site, '_yaml*.pyd')):
        shutil.copy(file, ff_site)
    print("已复制 yaml 相关文件到 ffpython site-packages")
    # 测试 ffpython 是否能 import yaml
    try:
        out = subprocess.check_output([
            ffpython_path, "-c", "import yaml; print(yaml.__version__)"
        ], encoding="utf-8")
        print(f"ffpython 成功 import yaml, 版本: {out.strip()}")
    except Exception as e:
        print(f"ffpython import yaml 失败: {e}")

def main():
    install_normal_packages()
    copy_pyyaml_to_ffpython()
    print("依赖安装流程结束。")

if __name__ == "__main__":
    main()
