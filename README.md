# 项目介绍：批量化格式年报文件  
  
## 怎么用：
- 先运行 text_process.py 是对错误文件进行错误分类的
- 后运行 text_formating.py 对文本进行格式化输出
- utlis 是 正则化的规则  
  

## 对text_process.py说明：

```
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
```

```
class Preprocess:
    # 1、Input_txt遍历年报文件，输出去除换行符的年报，是list类型
    # 2、寻找文章的名字、目录、章节题目、页眉
    #   _is_XX类型的函数是对遍历的每一行判断是什么类型
    #       类型：英语
    #       类型：目录
    #       类型：文章题目
    #   get_header类型是对全文进行句子频率统计，得出出现频率最高对前十个句子，若其中出现'年度报告',则判断是页眉
```
## 对text_formating进行说明
```
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
```
```
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
```# text_formating
