"""
官方 FontTools 的 OTF 到 TTF 转换实现
这个包封装了来自 FontTools 的官方 otf2ttf 实现
"""

from .otf2ttf import MAX_ERR, TTFont, otf_to_ttf, update_hmtx

__all__ = ['MAX_ERR', 'TTFont', 'otf_to_ttf', 'update_hmtx'] 
