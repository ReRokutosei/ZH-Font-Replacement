"""
进度显示模块
负责控制台进度条的显示
"""


def print_progress_bar(current, total, prefix='', suffix='', length=40):
    """
    打印进度条到控制台。
    """
    percent = f"{100 * (current / float(total)):.1f}" if total else '0.0'
    filled_length = int(length * current // total) if total else 0
    bar = '█' * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='')
    if current >= total:
        print() 