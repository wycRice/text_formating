import re

# 页脚是形如 1/150数字
# 页脚是形如 1 2 3 4 数字
# 页脚是形如 - 1 - ~ 1 ~
FOOTER_RES = [
    re.compile('[0-9]{1,3}[\u2002 ]{0,2}/[\u2002 ]{0,2}[0-9]{3}'),
    re.compile('^[0-9]{1,3}$'),
    re.compile('[-~][\u2002 ]{0,3}[0-9][\u2002 ]{0,3}-[-~]'),
]

# 判断句子前空格数
line_space_20 = re.compile('^[\u2002 ]{20,}')

# 查找句中三空格
tri_space = re.compile('\u2002\u2002\u2002|   ')
one_space = re.compile('[\u2002 ]')

# 查找 目录
CATALOG_TITLE = re.compile('^目[\u2002 ]*录|[\u2002 ]目[\u2002 ]*录[\u2002 ]*$')

# 查找 目录内容
CATALOG_RES = [
    re.compile('\.{6}'),
    re.compile('^第[一二三四五六七八九零十]{1,2}[节章].*\d$'),
    re.compile('^第[一二三四五六七八九零十]{1,2}[节章]'),
    re.compile('^[一二三四五六七八九零十]{1,2}、.*\d$'),
    re.compile('^[一二三四五六七八九零十]{1,2}、[\u4e00-\u9fa5]'),
    #re.compile('^[0-9].*\d$'),
    re.compile('^[一二三四五六七八九零十]{1,2}、.*\d]$'),
]

# 查找目录break
CATALOG_RES_BREAK = [
    re.compile('\u2002\u2002\u2002|   '),
    re.compile('[\u2002 ]*释[\u2002 ]*义$|^[\u2002 ]*释[\u2002 ]*义')
]
# 查找 章节标题
PARAGRAPH_TITLE_RES = [
    re.compile('^第[一二三四五六七八九零十]{1,2}[节章][\u2002 ]'),
    re.compile('^第[一二三四五六七八九零十]{1,2}[节章][\u4e00-\u9fa5、]+$'),
]

# 查找 题目
TITLE_RES = [
    re.compile('^第[0-9]{1,2}节'),
    re.compile('^[一二三四五六七八九零十百千万亿0-9]{1,2}、'),
    re.compile('^[0-9]{1,2}\.[0-9]?'),
    re.compile('^（[一二三四五六七八九零十百千万亿0-9]{1,2}）'),
    re.compile('^\([一二三四五六七八九零十百千万亿0-9a-zA-Z]{1,2}\)'),
]
# 查找 不属于题目的标点
PUNCTUATION = re.compile('[。：？；，《》]')

# 查找 中文
CHINESE = re.compile('[\u4e00-\u9fa5]')

# 查找 特殊符号
SPECIAL_RES = [
    re.compile('[□√]'),
    re.compile('单位：[\u2002 ]*元|单位：[\u2002 ]*万元|单位：[\u2002 ]*人民币'),
]

# 查找 表格
TABLE_RES = [
    re.compile('-+$'),
    re.compile('[《》\u4e00-\u9fa5、]*[\u2002 ]{3,}指[\u2002 ]{3,}[《》\u4e00-\u9fa5、]'), # ch  指 ch
    re.compile('^[\u2002]{15,}|[ ]{15,}'), # 开头有40个空格
    re.compile('^[\u4e00-\u9fa5、]*([\u2002 ]{3,}[\d,.%]){3,}'), # ch num num num
    re.compile('([\u2002 ]{3,}[\d,.%]){3,}'), # num num num
    re.compile('[\u4e00-\u9fa5、\d]*[\u2002 ]{38,}[\u4e00-\u9fa5、\d]*$')  # ch space ch
]