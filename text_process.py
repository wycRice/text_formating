import os, shutil
from collections import Counter
from utlis import *

def read_txtname(path):
    return [txt_name for txt_name in os.listdir(path)
            if txt_name.endswith('.txt')]

def num_to_ch(num):
    d ={0 : '零',
        1: '一',
             2: '二',
             3: '三',
             4: '四',
             5: '五',
             6: '六',
             7: '七',
             8: '八',
             9: '九',
             10: '十',
             11: '十一',
             12: '十二',
             13: '十三',
             14: '十四',
             15: '十五',
             16: '十六',
             17: '十七',
             18: '十八',
             19: '十九',
             20: '二十'}
    if  num < 21:
        return d[num]
    else:
        return False


class Preprocess:
    # 1、Input_txt遍历年报文件，输出去除换行符的年报，是list类型
    # 2、寻找文章的名字、目录、章节题目、页眉
    #   _is_XX类型的函数是对遍历的每一行判断是什么类型
    #       类型：英语
    #       类型：目录
    #       类型：文章题目
    #   get_header类型是对全文进行句子频率统计，得出出现频率最高对前十个句子，若其中出现'年度报告',则判断是页眉
    def __init__(self, txt_name, path):
        self.lines_striped = [] # 去除了句首空格
        self.Title = ''
        self.lines_nonstriped = self.Input_txt(txt_name, path)

        self.header = self._get_header()
        self.catalog = self._is_catalog()
        self.chapters_title = self._is_chapters_title()

    def Input_txt(self, txt_name, path):
        file = os.path.join(path, txt_name)

        with open(file, 'r', newline='',encoding='utf8') as f:
            lines = f.readlines()
            text = []
            for line in lines:
                line=line.split('\n')[0]
                line_striped=line.strip('\u2002')
                text.append(line)
                self.lines_striped.append(line_striped)
                if not self.Title:
                    self.Title = line
        return text

    def mv_txt(self, txt_name, path):
        file = os.path.join(path, txt_name)


        Engtxt = path + '/English_txt'
        Wrong1 = path + '/wrong_无目录_txt'
        Wrong2 = path + '/wrong_章节题目不全_txt'
        Wrong3 = path + '/wrong_章节题目过多_txt'

        if not os.path.exists(Engtxt):
            os.mkdir(Engtxt)
        if not os.path.exists(Wrong1):
            os.mkdir(Wrong1)
        if not os.path.exists(Wrong2):
            os.mkdir(Wrong2)
        if not os.path.exists(Wrong3):
            os.mkdir(Wrong3)


        if self._is_Eng():
            return shutil.move(file, Engtxt)
        ret = self._is_wrongtxt()
        if ret == 1:
            return shutil.move(file, Wrong1)
        if ret == 2:
            return shutil.move(file, Wrong2)
        if ret == 3:
            return shutil.move(file, Wrong3)

    def _is_wrongtxt(self):
        catalog  = self.catalog
        title = self._is_chapters_title()
        c_l, t_l = len(catalog), len(title)

        if not t_l: # 没有抽取到章节题目的情况
            return 2
        if num_to_ch(len(title)) is False:
            return 3
        if  num_to_ch(len(title)) not in title[-1]: # 章节题目不全
            return 2
        if not c_l: # 没有目录
            return 1

    #判定是否是英文文档
    def _is_Eng(self):
        lang=[1]
        length = len(self.lines_striped)
        begin, stop = int(0.01*length), int(0.21*length)
        for i, l in enumerate(self.lines_striped):
            if begin < i < stop:
                if  CHINESE.findall(l):
                    lang.append(False)
            if i > stop:
                break
        return all(lang) if len(lang) > int(0.05*length) else True
    #找目录
    def _is_catalog(self):
        catalog=[]
        index= 20

        for i, line in enumerate(self.lines_striped):
            if CATALOG_TITLE.search(line):
                index=i
                #print(line)
                break

        for line in self.lines_nonstriped[index+1: index+100]:
            line_striped = line.strip('\u2002 ')
            #print(line)
            headers = self.header
            if any(CATALOG_BREAK.match(line) for CATALOG_BREAK in CATALOG_RES_BREAK):
                if any(line_striped == header for header in headers) or any(footer.search(line_striped) for footer in FOOTER_RES) or CATALOG_RES[0].search(line):
                    continue
                break
            for CATALOG in CATALOG_RES:
                result = CATALOG.search(line_striped)
                if result:
                    catalog.append(line)
                    break

        if catalog and '二' in catalog[-1] and '十' not in catalog[-1]:
            del catalog[-1]
        if catalog and '一' in catalog[-1] and '十' not in catalog[-1]:
            del catalog[-1]

        return catalog

    def _is_chapters_title(self):
        para_titles = []
        for line in self.lines_nonstriped:
            line_striped = line.strip('\u2002 ')
            if line not in self.catalog:
                if PUNCTUATION.search(line_striped):
                    continue
                if any(para_title.search(line_striped) for para_title in PARAGRAPH_TITLE_RES):
                    para_titles.append(line_striped)
                    if num_to_ch(len(para_titles)) not in para_titles[-1]:
                        del para_titles[-1]
        return para_titles

    def _get_header(self):
        rows_counter = Counter(self.lines_striped)
        return [i[0] for i in rows_counter.most_common(10)
                if '年度报告' in i[0]]

    def processed_data(self):
        return self.lines_nonstriped, self.Title, self.header, self.catalog, self.chapters_title

def mv(path):
    # 1、获取文档中全部年报名字
    # 2、遍历年报
    # 3、对年报进行预处理，将不正确的年报移动到相应文件夹
    #   错误类型一：年报非简体汉字
    #   错误类型二：年报没有目录
    #   错误类型三：年报中有章节题目不全、或者缺失、或者命名不正确，比如有两个第十章
    #   错误类型四：年报中章节题目过多，将非章节题目的句子判断成章节题目
    txt_names = read_txtname(path)
    for i, txt_name in enumerate(txt_names):
        p = Preprocess(txt_name=txt_name, path=path)
        p.mv_txt(txt_name=txt_name, path=path)
        # title = p._is_chapters_title()
        # catalog = p.catalog
        # if not title:
        #     print('None')
        #     continue
        # if  num_to_ch(len(title)) is False or num_to_ch(len(title)) not in title[-1]:
        #     print(txt_name)
        #     print('title:', title, len(title))
        #     print('catalog:', catalog, len(catalog))
        if i % 100 ==0:
            print(i)

if __name__ == '__main__':
    path = '../data/Annual_Reports_TXT_2016_2017'
    mv(path)
