from fontTools.ttLib import TTFont
import config_utils
import datetime


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
    today = datetime.datetime.now().strftime('%B %d, %Y')
    version_str = f"Version {VERSION};{today}"

    font = TTFont(f'{TMP_DIR}/{src}')
    name_table = font['name']

    # 修改所有 nameID=5 的记录
    found = False
    for record in name_table.names:
        if record.nameID == 5:
            record.string = version_str.encode('utf-16-be')
            found = True
    # 若没有则添加
    if not found:
        from fontTools.ttLib.tables._n_a_m_e import NameRecord
        rec = NameRecord()
        rec.nameID = 5
        rec.platformID = 3
        rec.platEncID = 1
        rec.langID = 0x0409
        rec.string = version_str.encode('utf-16-be')
        name_table.names.append(rec)

    font.save(f'{DST_DIR}/{out}')


if __name__ == '__main__':
    for src, weight, out in RENAME_FONTS:
        set_names(src, weight, out)
