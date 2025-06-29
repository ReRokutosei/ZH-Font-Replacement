import fontforge as ff
import shutil as fs
import config_utils
import sys
import os
import datetime

config = config_utils.load_config()


def open_font(path):
    return ff.open(path)


def remove_gasp(font):
    font.gasp = ()


def set_cleartype(font):
    font.head_optimized_for_cleartype = 1


def get_version(font):
    # 获取原始版本号并拼接日期
    base = font.version.split(';')[0]
    today = datetime.datetime.now().strftime('%B %d, %Y')
    return f"{base};{today}"


def set_font_names(font, *, fontname, familyname, fullname, subfamily, copyright, version, zh_family=None, zh_fullname=None):
    font.fontname = fontname
    font.familyname = familyname
    font.fullname = fullname
    font.version = version
    font.copyright = copyright
    names = [
        ('English (US)', 'Family', familyname),
        ('English (US)', 'Fullname', fullname),
        ('English (US)', 'UniqueID', fullname),
        ('English (US)', 'SubFamily', subfamily),
        ('English (US)', 'Version', version),
        ('English (US)', 'Copyright', copyright),
    ]
    if zh_family:
        names.append(('Chinese (PRC)', 'Family', zh_family))
    if zh_fullname:
        names.append(('Chinese (PRC)', 'Fullname', zh_fullname))
    font.sfnt_names = tuple(names)


def gen_regular():
    src = os.path.join(config['TEMP_DIR'], config['REGULAR_SOURCE'] + '.ttf')
    ui = os.path.join(config['TEMP_DIR'], config['REGULAR_SOURCE'] + '-UI.ttf')
    fs.copy(src, ui)
    font = open_font(src)
    remove_gasp(font)
    set_cleartype(font)
    set_font_names(font,
        fontname='MicrosoftYaHei', familyname='Microsoft YaHei', fullname='Microsoft YaHei',
        subfamily='Regular', copyright=config['COPYRIGHT'], version=get_version(font),
        zh_family='微软雅黑', zh_fullname='微软雅黑')
    font_ui = open_font(ui)
    remove_gasp(font_ui)
    set_cleartype(font_ui)
    set_font_names(font_ui,
        fontname='MicrosoftYaHeiUI', familyname='Microsoft YaHei UI', fullname='Microsoft YaHei UI',
        subfamily='Regular', copyright=config['COPYRIGHT'], version=get_version(font_ui),
        zh_family='微软雅黑 UI', zh_fullname='微软雅黑 UI')
    font.generateTtc(os.path.join(config['TEMP_DIR'], 'msyh.ttc'), font_ui, ttcflags=('merge'), layer=1)


def gen_bold():
    src = os.path.join(config['TEMP_DIR'], config['BOLD_SOURCE'] + '.ttf')
    ui = os.path.join(config['TEMP_DIR'], config['BOLD_SOURCE'] + '-UI.ttf')
    fs.copy(src, ui)
    font = open_font(src)
    remove_gasp(font)
    set_cleartype(font)
    set_font_names(font,
        fontname='MicrosoftYaHeiBold', familyname='Microsoft YaHei', fullname='Microsoft YaHei Bold',
        subfamily='Bold', copyright=config['COPYRIGHT'], version=get_version(font),
        zh_family='微软雅黑', zh_fullname='微软雅黑 Bold')
    font_ui = open_font(ui)
    remove_gasp(font_ui)
    set_cleartype(font_ui)
    set_font_names(font_ui,
        fontname='MicrosoftYaHeiUIBold', familyname='Microsoft YaHei UI', fullname='Microsoft YaHei UI Bold',
        subfamily='Bold', copyright=config['COPYRIGHT'], version=get_version(font_ui),
        zh_family='微软雅黑 UI', zh_fullname='微软雅黑 UI Bold')
    font.generateTtc(os.path.join(config['TEMP_DIR'], 'msyhbd.ttc'), font_ui, ttcflags=('merge'), layer=1)


def gen_light():
    src = os.path.join(config['TEMP_DIR'], config['LIGHT_SOURCE'] + '.ttf')
    ui = os.path.join(config['TEMP_DIR'], config['LIGHT_SOURCE'] + '-UI.ttf')
    fs.copy(src, ui)
    font = open_font(src)
    remove_gasp(font)
    set_cleartype(font)
    set_font_names(font,
        fontname='MicrosoftYaHeiLight', familyname='Microsoft YaHei', fullname='Microsoft YaHei Light',
        subfamily='Light', copyright=config['COPYRIGHT'], version=get_version(font),
        zh_family='微软雅黑', zh_fullname='微软雅黑 Light')
    font_ui = open_font(ui)
    remove_gasp(font_ui)
    set_cleartype(font_ui)
    set_font_names(font_ui,
        fontname='MicrosoftYaHeiUILight', familyname='Microsoft YaHei UI', fullname='Microsoft YaHei UI Light',
        subfamily='Light', copyright=config['COPYRIGHT'], version=get_version(font_ui),
        zh_family='微软雅黑 UI', zh_fullname='微软雅黑 UI Light')
    font.generateTtc(os.path.join(config['TEMP_DIR'], 'msyhl.ttc'), font_ui, ttcflags=('merge'), layer=1)


def gen_extralight():
    src = os.path.join(config['TEMP_DIR'], config['EXTRALIGHT_SOURCE'] + '.ttf')
    ui = os.path.join(config['TEMP_DIR'], config['EXTRALIGHT_SOURCE'] + '-UI.ttf')
    fs.copy(src, ui)
    font = open_font(src)
    remove_gasp(font)
    set_cleartype(font)
    set_font_names(font,
        fontname='MicrosoftYaHeiExtraLight', familyname='Microsoft YaHei', fullname='Microsoft YaHei ExtraLight',
        subfamily='ExtraLight', copyright=config['COPYRIGHT'], version=get_version(font),
        zh_family='微软雅黑', zh_fullname='微软雅黑 ExtraLight')
    font_ui = open_font(ui)
    remove_gasp(font_ui)
    set_cleartype(font_ui)
    set_font_names(font_ui,
        fontname='MicrosoftYaHeiUIExtraLight', familyname='Microsoft YaHei UI', fullname='Microsoft YaHei UI ExtraLight',
        subfamily='ExtraLight', copyright=config['COPYRIGHT'], version=get_version(font_ui),
        zh_family='微软雅黑 UI', zh_fullname='微软雅黑 UI ExtraLight')
    font.generateTtc(os.path.join(config['TEMP_DIR'], 'msyhel.ttc'), font_ui, ttcflags=('merge'), layer=1)


def gen_semibold():
    src = os.path.join(config['TEMP_DIR'], config['SEMIBOLD_SOURCE'] + '.ttf')
    ui = os.path.join(config['TEMP_DIR'], config['SEMIBOLD_SOURCE'] + '-UI.ttf')
    fs.copy(src, ui)
    font = open_font(src)
    remove_gasp(font)
    set_cleartype(font)
    set_font_names(font,
        fontname='MicrosoftYaHeiSemibold', familyname='Microsoft YaHei', fullname='Microsoft YaHei Semibold',
        subfamily='SemiBold', copyright=config['COPYRIGHT'], version=get_version(font),
        zh_family='微软雅黑', zh_fullname='微软雅黑 SemiBold')
    font_ui = open_font(ui)
    remove_gasp(font_ui)
    set_cleartype(font_ui)
    set_font_names(font_ui,
        fontname='MicrosoftYaHeiUISemibold', familyname='Microsoft YaHei UI', fullname='Microsoft YaHei UI Semibold',
        subfamily='SemiBold', copyright=config['COPYRIGHT'], version=get_version(font_ui),
        zh_family='微软雅黑 UI', zh_fullname='微软雅黑 UI SemiBold')
    font.generateTtc(os.path.join(config['TEMP_DIR'], 'msyhsb.ttc'), font_ui, ttcflags=('merge'), layer=1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        func = sys.argv[1]
        if func == "gen_regular":
            gen_regular()
        elif func == "gen_bold":
            gen_bold()
        elif func == "gen_light":
            gen_light()
        elif func == "gen_extralight":
            gen_extralight()
        elif func == "gen_semibold":
            gen_semibold()
