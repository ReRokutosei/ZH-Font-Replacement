"""
配置管理模块
负责配置文件的加载、验证和参数获取
"""

import logging
import os
import yaml


def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    with open(config_path, encoding='utf-8') as f:
        config = yaml.safe_load(f)
    if not isinstance(config, dict):
        raise RuntimeError(f"config.yaml 解析异常，返回类型: {type(config)}, 内容: {config}")
    return config


def validate_config(config):
    """验证配置参数"""
    if not config.get('ENABLE_MS_YAHEI', True) and not config.get('ENABLE_SEGOE_UI', True):
        logging.error("错误：至少需要启用一项生成功能（微软雅黑/Segoe UI）")
        raise SystemExit(1)


def get_config_value(config, key, default=None):
    """
    获取配置参数，若不存在则返回默认值。
    """
    return config[key] if key in config else default 