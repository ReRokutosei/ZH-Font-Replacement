import fontforge as ff
import shutil as fs
import auto_configs as conf
import sys


def open_font(path):
    return ff.open(path)


def remove_gasp(font):
    font.gasp = ()


def set_cleartype(font):
    font.head_optimized_for_cleartype = 1


def get_version(font):
    return font.version.split(';')[0]


def set_regular_names(font):
    font.fontname = 'MicrosoftYaHei'
    font.familyname = 'Microsoft YaHei'
    font.fullname = 'Microsoft YaHei'
    font.version = get_version(font)
    font.copyright = conf.COPYRIGHT
    font.sfnt_names = (
        ('English (US)', 'Family', 'Microsoft YaHei'),
        ('English (US)', 'Fullname', 'Microsoft YaHei'),
        ('English (US)', 'UniqueID', 'Microsoft YaHei'),
        ('English (US)', 'SubFamily', 'Regular'),
        ('English (US)', 'Version', get_version(font)),
        ('English (US)', 'Copyright', conf.COPYRIGHT),
        ('Chinese (PRC)', 'Family', '微软雅黑'),
        ('Chinese (PRC)', 'Fullname', '微软雅黑')
    )


def set_regular_ui_names(font):
    font.fontname = 'MicrosoftYaHeiUI'
    font.familyname = 'Microsoft YaHei UI'
    font.fullname = 'Microsoft YaHei UI'
    font.version = get_version(font)
    font.copyright = conf.COPYRIGHT
    font.sfnt_names = (
        ('English (US)', 'Family', 'Microsoft YaHei UI'),
        ('English (US)', 'Fullname', 'Microsoft YaHei UI'),
        ('English (US)', 'UniqueID', 'Microsoft YaHei UI'),
        ('English (US)', 'SubFamily', 'Regular'),
        ('English (US)', 'Version', get_version(font)),
        ('English (US)', 'Copyright', conf.COPYRIGHT),
        ('Chinese (PRC)', 'Family', '微软雅黑 UI'),
        ('Chinese (PRC)', 'Fullname', '微软雅黑 UI')
    )


def set_bold_names(font):
    font.fontname = 'MicrosoftYaHeiBold'
    font.familyname = 'Microsoft YaHei'
    font.fullname = 'Microsoft YaHei Bold'
    font.version = get_version(font)
    font.copyright = conf.COPYRIGHT
    font.sfnt_names = (
        ('English (US)', 'Family', 'Microsoft YaHei'),
        ('English (US)', 'Fullname', 'Microsoft YaHei Bold'),
        ('English (US)', 'UniqueID', 'Microsoft YaHei Bold'),
        ('English (US)', 'SubFamily', 'Bold'),
        ('English (US)', 'Version', get_version(font)),
        ('English (US)', 'Copyright', conf.COPYRIGHT),
        ('Chinese (PRC)', 'Family', '微软雅黑'),
        ('Chinese (PRC)', 'Fullname', '微软雅黑 Bold')
    )


def set_bold_ui_names(font):
    font.fontname = 'MicrosoftYaHeiUIBold'
    font.familyname = 'Microsoft YaHei UI'
    font.fullname = 'Microsoft YaHei UI Bold'
    font.version = get_version(font)
    font.copyright = conf.COPYRIGHT
    font.sfnt_names = (
        ('English (US)', 'Family', 'Microsoft YaHei UI'),
        ('English (US)', 'Fullname', 'Microsoft YaHei UI Bold'),
        ('English (US)', 'UniqueID', 'Microsoft YaHei UI Bold'),
        ('English (US)', 'SubFamily', 'Bold'),
        ('English (US)', 'Version', get_version(font)),
        ('English (US)', 'Copyright', conf.COPYRIGHT),
        ('Chinese (PRC)', 'Family', '微软雅黑 UI'),
        ('Chinese (PRC)', 'Fullname', '微软雅黑 UI Bold')
    )


def set_light_names(font):
    font.fontname = 'MicrosoftYaHeiLight'
    font.familyname = 'Microsoft YaHei'
    font.fullname = 'Microsoft YaHei Light'
    font.version = get_version(font)
    font.copyright = conf.COPYRIGHT
    font.sfnt_names = (
        ('English (US)', 'Family', 'Microsoft YaHei'),
        ('English (US)', 'Fullname', 'Microsoft YaHei Light'),
        ('English (US)', 'UniqueID', 'Microsoft YaHei Light'),
        ('English (US)', 'SubFamily', 'Light'),
        ('English (US)', 'Version', get_version(font)),
        ('English (US)', 'Copyright', conf.COPYRIGHT),
        ('Chinese (PRC)', 'Family', '微软雅黑'),
        ('Chinese (PRC)', 'Fullname', '微软雅黑 Light')
    )


def set_light_ui_names(font):
    font.fontname = 'MicrosoftYaHeiUILight'
    font.familyname = 'Microsoft YaHei UI'
    font.fullname = 'Microsoft YaHei UI Light'
    font.version = get_version(font)
    font.copyright = conf.COPYRIGHT
    font.sfnt_names = (
        ('English (US)', 'Family', 'Microsoft YaHei UI'),
        ('English (US)', 'Fullname', 'Microsoft YaHei UI Light'),
        ('English (US)', 'UniqueID', 'Microsoft YaHei UI Light'),
        ('English (US)', 'SubFamily', 'Light'),
        ('English (US)', 'Version', get_version(font)),
        ('English (US)', 'Copyright', conf.COPYRIGHT),
        ('Chinese (PRC)', 'Family', '微软雅黑 UI'),
        ('Chinese (PRC)', 'Fullname', '微软雅黑 UI Light')
    )


def set_extralight_names(font):
    font.fontname = 'MicrosoftYaHeiExtraLight'
    font.familyname = 'Microsoft YaHei'
    font.fullname = 'Microsoft YaHei ExtraLight'
    font.version = get_version(font)
    font.copyright = conf.COPYRIGHT
    font.sfnt_names = (
        ('English (US)', 'Family', 'Microsoft YaHei'),
        ('English (US)', 'Fullname', 'Microsoft YaHei ExtraLight'),
        ('English (US)', 'UniqueID', 'Microsoft YaHei ExtraLight'),
        ('English (US)', 'SubFamily', 'ExtraLight'),
        ('English (US)', 'Version', get_version(font)),
        ('English (US)', 'Copyright', conf.COPYRIGHT),
        ('Chinese (PRC)', 'Family', '微软雅黑'),
        ('Chinese (PRC)', 'Fullname', '微软雅黑 ExtraLight')
    )


def set_extralight_ui_names(font):
    font.fontname = 'MicrosoftYaHeiUIExtraLight'
    font.familyname = 'Microsoft YaHei UI'
    font.fullname = 'Microsoft YaHei UI ExtraLight'
    font.version = get_version(font)
    font.copyright = conf.COPYRIGHT
    font.sfnt_names = (
        ('English (US)', 'Family', 'Microsoft YaHei UI'),
        ('English (US)', 'Fullname', 'Microsoft YaHei UI ExtraLight'),
        ('English (US)', 'UniqueID', 'Microsoft YaHei UI ExtraLight'),
        ('English (US)', 'SubFamily', 'ExtraLight'),
        ('English (US)', 'Version', get_version(font)),
        ('English (US)', 'Copyright', conf.COPYRIGHT),
        ('Chinese (PRC)', 'Family', '微软雅黑 UI'),
        ('Chinese (PRC)', 'Fullname', '微软雅黑 UI ExtraLight')
    )


def set_semibold_names(font):
    font.fontname = 'MicrosoftYaHeiSemibold'
    font.familyname = 'Microsoft YaHei'
    font.fullname = 'Microsoft YaHei Semibold'
    font.version = get_version(font)
    font.copyright = conf.COPYRIGHT
    font.sfnt_names = (
        ('English (US)', 'Family', 'Microsoft YaHei'),
        ('English (US)', 'Fullname', 'Microsoft YaHei Semibold'),
        ('English (US)', 'UniqueID', 'Microsoft YaHei Semibold'),
        ('English (US)', 'SubFamily', 'SemiBold'),
        ('English (US)', 'Version', get_version(font)),
        ('English (US)', 'Copyright', conf.COPYRIGHT),
        ('Chinese (PRC)', 'Family', '微软雅黑'),
        ('Chinese (PRC)', 'Fullname', '微软雅黑 SemiBold')
    )


def set_semibold_ui_names(font):
    font.fontname = 'MicrosoftYaHeiUISemibold'
    font.familyname = 'Microsoft YaHei UI'
    font.fullname = 'Microsoft YaHei UI Semibold'
    font.version = get_version(font)
    font.copyright = conf.COPYRIGHT
    font.sfnt_names = (
        ('English (US)', 'Family', 'Microsoft YaHei UI'),
        ('English (US)', 'Fullname', 'Microsoft YaHei UI Semibold'),
        ('English (US)', 'UniqueID', 'Microsoft YaHei UI Semibold'),
        ('English (US)', 'SubFamily', 'SemiBold'),
        ('English (US)', 'Version', get_version(font)),
        ('English (US)', 'Copyright', conf.COPYRIGHT),
        ('Chinese (PRC)', 'Family', '微软雅黑 UI'),
        ('Chinese (PRC)', 'Fullname', '微软雅黑 UI SemiBold')
    )


def gen_regular():
    fs.copy(conf.TEMP_DIR + '/' + conf.REGULAR_SOURCE + '.ttf',
            conf.TEMP_DIR + '/' + conf.REGULAR_SOURCE + '-UI.ttf')

    font = open_font(conf.TEMP_DIR + '/' + conf.REGULAR_SOURCE + '.ttf')
    remove_gasp(font)
    set_cleartype(font)
    set_regular_names(font)

    font_ui = open_font(conf.TEMP_DIR + '/' +
                        conf.REGULAR_SOURCE + '-UI.ttf')
    remove_gasp(font_ui)
    set_cleartype(font_ui)
    set_regular_ui_names(font_ui)

    font.generateTtc(conf.TEMP_DIR + '/msyh.ttc',
                     font_ui, ttcflags=('merge'), layer=1)


def gen_bold():
    fs.copy(conf.TEMP_DIR + '/' + conf.BOLD_SOURCE + '.ttf',
            conf.TEMP_DIR + '/' + conf.BOLD_SOURCE + '-UI.ttf')

    font = open_font(conf.TEMP_DIR + '/' + conf.BOLD_SOURCE + '.ttf')
    remove_gasp(font)
    set_cleartype(font)
    set_bold_names(font)

    font_ui = open_font(conf.TEMP_DIR + '/' + conf.BOLD_SOURCE + '-UI.ttf')
    remove_gasp(font_ui)
    set_cleartype(font_ui)
    set_bold_ui_names(font_ui)

    font.generateTtc(conf.TEMP_DIR + '/msyhbd.ttc',
                     font_ui, ttcflags=('merge'), layer=1)


def gen_light():
    fs.copy(conf.TEMP_DIR + '/' + conf.LIGHT_SOURCE + '.ttf',
            conf.TEMP_DIR + '/' + conf.LIGHT_SOURCE + '-UI.ttf')

    font = open_font(conf.TEMP_DIR + '/' + conf.LIGHT_SOURCE + '.ttf')
    remove_gasp(font)
    set_cleartype(font)
    set_light_names(font)

    font_ui = open_font(conf.TEMP_DIR + '/' +
                        conf.LIGHT_SOURCE + '-UI.ttf')
    remove_gasp(font_ui)
    set_cleartype(font_ui)
    set_light_ui_names(font_ui)

    font.generateTtc(conf.TEMP_DIR + '/msyhl.ttc',
                     font_ui, ttcflags=('merge'), layer=1)


def gen_extralight():
    fs.copy(conf.TEMP_DIR + '/' + conf.EXTRALIGHT_SOURCE + '.ttf',
            conf.TEMP_DIR + '/' + conf.EXTRALIGHT_SOURCE + '-UI.ttf')

    font = open_font(conf.TEMP_DIR + '/' + conf.EXTRALIGHT_SOURCE + '.ttf')
    remove_gasp(font)
    set_cleartype(font)
    set_extralight_names(font)

    font_ui = open_font(conf.TEMP_DIR + '/' + conf.EXTRALIGHT_SOURCE + '-UI.ttf')
    remove_gasp(font_ui)
    set_cleartype(font_ui)
    set_extralight_ui_names(font_ui)

    font.generateTtc(conf.TEMP_DIR + '/msyhel.ttc',
                     font_ui, ttcflags=('merge'), layer=1)


def gen_semibold():
    fs.copy(conf.TEMP_DIR + '/' + conf.SEMIBOLD_SOURCE + '.ttf',
            conf.TEMP_DIR + '/' + conf.SEMIBOLD_SOURCE + '-UI.ttf')

    font = open_font(conf.TEMP_DIR + '/' + conf.SEMIBOLD_SOURCE + '.ttf')
    remove_gasp(font)
    set_cleartype(font)
    set_semibold_names(font)

    font_ui = open_font(conf.TEMP_DIR + '/' + conf.SEMIBOLD_SOURCE + '-UI.ttf')
    remove_gasp(font_ui)
    set_cleartype(font_ui)
    set_semibold_ui_names(font_ui)

    font.generateTtc(conf.TEMP_DIR + '/msyhsb.ttc',
                     font_ui, ttcflags=('merge'), layer=1)


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
