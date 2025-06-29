from fontTools.ttLib import TTFont
import config_utils


config = config_utils.load_config()

TMP_DIR = config.get('TEMP_DIR', './temp')
DST_DIR = config.get('RESULT_DIR', './result')
VERSION = '2503'
COPYRIGHT = config.get('COPYRIGHT', 'Made from sarasa by chenh')


RENAME_FONTS = [
    ('SarasaMonoSC-Regular.ttf', 'Regular', 'HansCode-Regular.ttf'),
    ('SarasaMonoSC-Bold.ttf', 'Bold', 'HansCode-Bold.ttf'),
    ('SarasaMonoSC-Italic.ttf', 'Italic', 'HansCode-Italic.ttf'),
    ('SarasaMonoSC-BoldItalic.ttf', 'Bold Italic', 'HansCode-BoldItalic.ttf')
]


def set_names(src, weight, out):
    family_name = 'HansCode'
    font_name = f'HansCode{weight}'

    font = TTFont(f'{TMP_DIR}/{src}')
    name_table = font['name']

    # 清除原有 name 记录
    del name_table.names[:]
    # 添加新 name 记录
    name_table.setName(COPYRIGHT, 0, 3, 1, 0x0409)
    name_table.setName(family_name, 1, 3, 1, 0x0409)
    name_table.setName(weight, 2, 3, 1, 0x0409)
    name_table.setName(font_name, 3, 3, 1, 0x0409)
    name_table.setName(font_name, 4, 3, 1, 0x0409)
    name_table.setName(VERSION, 5, 3, 1, 0x0409)
    name_table.setName(font_name, 6, 3, 1, 0x0409)

    font.save(f'{DST_DIR}/{out}')


if __name__ == '__main__':
    for src, weight, out in RENAME_FONTS:
        set_names(src, weight, out)
