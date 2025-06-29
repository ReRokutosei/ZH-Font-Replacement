import fontforge as ff
import shutil as fs
import config_utils
import sys
import os

config = config_utils.load_config()


def open_font(path):
    return ff.open(path)


def remove_gasp(font):
    font.gasp = ()


def set_cleartype(font):
    font.head_optimized_for_cleartype = 1


def get_version(font):
    return font.version.split(';')[0]


def set_font_names(font, *, fontname, familyname, fullname, subfamily, copyright, version, zh_family=None, zh_fullname=None, postscript=None):
    font.fontname = fontname
    font.familyname = familyname
    font.fullname = fullname
    font.version = version
    font.copyright = copyright
    names = [
        ('English (US)', 'Copyright', copyright),
        ('English (US)', 'Family', familyname),
        ('English (US)', 'SubFamily', subfamily),
        ('English (US)', 'UniqueID', fullname),
        ('English (US)', 'Fullname', fullname),
        ('English (US)', 'Version', version),
    ]
    if postscript:
        names.append(('English (US)', 'PostScriptName', postscript))
    if zh_family:
        names.append(('Chinese (PRC)', 'Family', zh_family))
    if zh_fullname:
        names.append(('Chinese (PRC)', 'Fullname', zh_fullname))
    font.sfnt_names = tuple(names)


def gen_simsun_ttc():
    src = os.path.join(config['TEMP_DIR'], config['SIMSUN_SOURCE'] + '.ttf')
    new = os.path.join(config['TEMP_DIR'], config['SIMSUN_SOURCE'] + '-New.ttf')
    fs.copy(src, new)
    font = open_font(src)
    remove_gasp(font)
    set_cleartype(font)
    set_font_names(font,
        fontname='SimSun', familyname='SimSun', fullname='SimSun', subfamily='Regular',
        copyright=config['COPYRIGHT'], version=get_version(font), postscript='SimSun',
        zh_family='宋体', zh_fullname='宋体')
    font_ui = open_font(new)
    remove_gasp(font_ui)
    set_cleartype(font_ui)
    set_font_names(font_ui,
        fontname='NSimSun', familyname='NSimSun', fullname='NSimSun', subfamily='Regular',
        copyright=config['COPYRIGHT'], version=get_version(font_ui), postscript='NSimSun',
        zh_family='新宋体', zh_fullname='新宋体')
    font.generateTtc(os.path.join(config['TEMP_DIR'], 'simsun.ttc'), font_ui, ttcflags=('merge'), layer=1)


def gen_simsun_ext():
    src = os.path.join(config['TEMP_DIR'], config['SIMSUN_SOURCE'] + '.ttf')
    font = open_font(src)
    remove_gasp(font)
    set_cleartype(font)
    set_font_names(font,
        fontname='SimSun-ExtB', familyname='SimSun-ExtB', fullname='SimSun-ExtB', subfamily='Regular',
        copyright=config['COPYRIGHT'], version=get_version(font), postscript='SimSun-ExtB')
    font.generate(os.path.join(config['TEMP_DIR'], 'simsunb.ttf'))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        func = sys.argv[1]
        if func == "gen_simsun_ttc":
            gen_simsun_ttc()
        elif func == "gen_simsun_ext":
            gen_simsun_ext()
