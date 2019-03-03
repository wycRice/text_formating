# 读取文件

import os, shutil
import re
import pandas as pd

from text_process import Preprocess, read_txtname
from utlis import *


# 提取文本
class ContentExtractor:
    # is_XX类型的函数是对遍历的每一行判断是什么类型
    #   页眉页脚 （判定是，则忽略此行）
    #   长度规则
    #   句末有标点
    #   文章章节题目 （由text_process输入）
    #   文章总标题 （由text_process输入）
    #   文章小题目及分论点
    #   文章表格判定
    #   年报特例

    def __init__(self, rows, header=None, catalog=None, chapters_title=None, Title=None):
        self.rows = rows
        self.header = header
        self.catalog = catalog
        self.Title = Title
        self.chapters_title = chapters_title

        self.sep='\u2002'

        self._ignore_rules = self._build_ignore_rules()
        self._break_rules = self._build_break_rules()
        self._strongbreak_rules = self._build_strong_break_rules()

    # 是页眉 句频最高的句子
    def _is_header(self, line, line_striped):
        return True if any(line_striped == header for header in self.header) else False
    # 是页脚
    def _is_footer(self, line, line_striped):
        if any(footer.search(line_striped) for footer in FOOTER_RES):
            return True
    # 长度规则，主要判断是否是表格和分栏数据
    def _length_rule(self, line, line_striped):
        # 被断行的一般都是字数到达一定程度自动换行，通过观察，一般都在40-50的长度
        # 有个别行在范围外，所以将阈值定在30-60
        # 特别长的一般都是目录和表格内的数据
        length = len(line)
        if length < 30 or length >68:
            return True
        if length > 58 and tri_space.findall(line_striped) \
            or line_space_20.search(line):
                return True
        return False
    # 句末标点
    def _is_end(self, line, line_striped):
        # 如果是句号(。)和冒号(：)结尾，认为是一个完整句
        return True if line[-1] in ['。', '：', '？','；','、','《','》'] else False

    # 每一个年报的 第一章 第二章的 题目
    def _is_chapters_title(self, line, line_striped):
        return True if line_striped in self.chapters_title else False

    # 每个年报的题目
    def _is_catalog(self, line, line_striped):
        return True if line_striped in self.catalog else False

    # 小标题、分论点 题目
    def _is_title(self, line, line_striped):
        if not PUNCTUATION.findall(line_striped):
            if any(TITLE.search(line_striped) for TITLE in TITLE_RES):
                return True

    def _is_item(self, line, line_striped):
        # '-'打头的可能是列表中的一项，如以'；'结尾，自成一段
        return re.search('^-.*；$', line_striped)

    # 表格判断
    def _is_table_row(self, line, line_striped):
        # for i, TABLE in enumerate(TABLE_RES):
        #     print(i)
        #     if TABLE.search(line):
        #         print(i)
        #         return True
        if any(TABLE.search(line) for TABLE in TABLE_RES ):
            return True

    # 年报特殊例子
    def _is_special(self, line, line_striped):
        if any(SPECIAL.search(line_striped) for SPECIAL in SPECIAL_RES):
            return True

    def _build_ignore_rules(self):
        rules = [
            self._is_header,
            self._is_footer
        ]
        return rules

    def _build_break_rules(self):
        rules = [
            self._length_rule,
            self._is_end,
            self._is_catalog,
            self._is_title,
            self._is_chapters_title,
            self._is_item,
            self._is_table_row,
        ]
        return rules

    def _build_strong_break_rules(self):
        rules = [
            self._is_chapters_title,
            self._is_special,
        ]
        return rules

    def get_text(self):
        temp = ''
        for line in self.rows:
            line_striped = line.strip(self.sep)
            if any(rule(line, line_striped) for rule in self._ignore_rules):
                continue
            if any(rule(line, line_striped) for rule in self._strongbreak_rules):
                if temp:
                    yield temp
                    yield line
                    temp = ''
                    continue
            if any(rule(line, line_striped) for rule in self._break_rules):
                temp += line
                yield temp
                temp = ''
            else:
                temp += line_striped

    def _get_chapters(self):
        tmp = ''
        for line in self.get_text():
            line = line.strip(self.sep)
            if self._is_chapters_title(line):
                yield(tmp)
                tmp = line + os.linesep
            else:
                tmp += line + os.linesep
        yield(tmp)

    def output(self, txt_name,  path, op='txt', root='output'):
        root = path + '/' + root
        #print('root:', root)
        if not os.path.exists(root):
            os.mkdir(root)

        if op == 'txt':
            return self.output_txt(txt_name, root)
        if op == 'csv':
            return self.output_csv(txt_name, root)

    def output_csv(self, txt_name, root):
        output_path = f'{root}/' + txt_name[:-4] + '.csv'
        print(output_path)
        df = pd.DataFrame(columns=['code', 'date', 'ID', 'Title', 'chapter', 'text'])

        catalog = self.catalog
        chapters = self._get_chapters()
        code, date, ID, Title = txt_name.split('-')[0], txt_name.split('-')[1], txt_name.split('-')[-1][-4], self.Title

        try:
            for i, chapter in enumerate(chapters):
                if i == 0: continue
                df.loc[i] = [code, date, ID, Title, (f'第{i}节'), (chapter)]
            df.to_csv(output_path, encoding="utf_8_sig", index=False)
        except IndexError:
            print(txt_name)

    def output_txt(self, txt_name, root):
        output_path =  root + '/' + txt_name

        with open(output_path, 'w', encoding='utf8') as f:
            for row in self.get_text():
                f.write(row + os.linesep)

def main(path):
    # 1、读取文件夹文件名
    # 2、遍历文件夹内每个年报
    # 3、对每个年报进行预处理，获得（下面年报指遍历的当前的年报）
    #   rows 去掉了所有换行符的年报，年报是一个list
    #   Title 年报第一句话就是题目
    #   header 年报的页眉
    #   catalog 年报的目录
    #   chapters_title 年报章节的题目，用于csv的分章节输出
    # 4、将上述预处理数据输入ContentExtrator
    # 5、输出
    #   参数三：可选输出'csv'和'txt'格式，
    #   参数四：输出文件夹名字
    txt_names = read_txtname(path)
    for i, txt_name in enumerate(txt_names):
        file = os.path.join(path, txt_name)

        p = Preprocess(txt_name=txt_name, path=path)
        rows, Title, header, catalog, chapters_title = p.processed_data()

        extractor = ContentExtractor(rows, header, catalog, chapters_title, Title)
        extractor.output(txt_name, path, 'txt', 'output_txt')
        if i  %100 == 0:
            print(i)

if __name__ == '__main__':
    path = '../data/Annual_Reports_TXT_2016_2017'
    main(path)


