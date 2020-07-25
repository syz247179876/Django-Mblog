import json
import os
from collections import Counter
from operator import itemgetter
from operator import methodcaller

import numpy as np
import pandas as pd

from mblog.celery import app
import re
from pathlib import Path
import logging

logger = logging.getLogger('visualize')


class Get_data_score:
    def __init__(self, IO):
        """
        初始化文件名
        """
        self.IO = IO
        self.data = None
        self.__columns = None
        self.__index = None

    @property
    def columns(self):
        return self.__columns

    @columns.setter
    def columns(self, columns):
        self.__column = columns

    @property
    def index(self):
        return self.__index

    @index.setter
    def index(self, index):
        self.__index = index

    def get_csv(self):
        self.data = pd.read_csv(self.IO)
        self.columns = self.data.columns
        self.index = self.data.index
        return self.data

    def get_excel(self):
        self.data = pd.read_excel(self.IO)
        self.__columns = self.data.columns
        self.__index = self.data.index
        return self.data

    def __iter__(self):
        return [i for i in self.__index]

    def __repr__(self):
        return self.IO

    def __call__(self):
        print('开始获取数据....')

    def __len__(self):
        """获取数据对象长度"""
        return len(self.__index)

    def method_trans(method_name, parmas):
        """自行构建函数"""
        method = methodcaller(method_name)
        return method(parmas)

    def modify_col(self, list_columns):
        """
        修改列
        """
        self.data = self.data.iloc[1:-2]
        self.data.columns = self.data.iloc[0]
        for i in self.data.columns:
            if '，' in i:
                i = (str(i).split('，')[0])
            list_columns.append(i)
        self.data.columns = list_columns
        self.data.drop(columns=['平均学分绩点'], axis=1, inplace=True)
        return self.data[1:]

    def modify_index(self):
        """
        修改索引
        """
        self.data.reindex(np.arange(1, 222))

    def get_first_name(self):
        """
        获取第一名的score
        :return: 姓名
        """
        name = self.get_first_infor()[1]
        return name

    def get_first_score(self):
        """获取第一名的分数"""
        score = self.get_first_infor()[3:-6]
        score = [float(i) if type(i) == str else round(i, 3) for i in score]
        return score

    def get_first_infor(self):
        """获取第一的信息"""
        first = self.data.iloc[0, :]
        return first.values

    def get_columns(self):
        """获取比较的列"""
        return tuple(self.data.columns[3:-6])

    @staticmethod
    def get_my_infor(df):
        """获取我的成绩信息"""
        xh = '17408002125'
        xm = '司云中'
        my_infor = df.data[df.data['学号'] == xh]
        return my_infor.values

    @staticmethod
    def get_my_name():
        return '司云中'


def get_my_score(df):
    my_score = df.get_my_infor(df)[0][3:-6]
    my_score = [float(i) if type(i) == str else round(i, 1) for i in my_score]
    return my_score


def get_data_score():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    IO = os.path.join(BASE_DIR, 'static/file/software.xls').replace('\\', '/')
    df = Get_data_score(IO)
    return df


def process(data_object):
    """
    数据清洗
    :param data_object:dataframe对象
    :return:清洗好的数据
    """
    col = []
    # data_object()
    data_object.get_excel()  # 获取初始data
    data_object.data = data_object.modify_col(col)
    data_object.modify_index()
    data_object.data = data_object.data.reset_index(drop=True)  # 重置从0开始的index下标
    return data_object.data


def get_all_information():
    df = get_data_score()
    process(df)  # 获取清洗过得数据
    first_data = df.get_first_infor()  # 获取第一名成绩信息
    first_name = df.get_first_name()
    first_score = df.get_first_score()
    my_data = df.get_my_infor(df)  # 获取我的成绩
    my_name = df.get_my_name()
    my_score = get_my_score(df)
    columns = df.get_columns()
    compare = {
        'first_data': first_data,
        'first_name': first_name,
        'first_score': first_score,
        'my_data': my_data,
        'my_name': my_name,
        'my_score': my_score,
        'columns': columns
    }
    return compare


class analysis_lagou:
    """
    对拉钩网的数据分析
    """
    KEYWORDS = ('python', 'java', 'c#', 'c++', 'web')
    CITY_NAME = ('北京', '上海', '深圳', '广州', '杭州', '成都', '南京', '武汉', '西安', '厦门', '长沙', '苏州', '天津')

    def __init__(self, file):
        self.file = file
        self.lagou = pd.read_csv(self.file)
        self.type = type(self.lagou)
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def __repr__(self):
        return '拉勾网数据分析'

    def first_clean(self):
        """
        初步清理数据
        """
        self.lagou.drop_duplicates(inplace=True)
        self.lagou.rename(columns={'city': '城市', 'education': '学历', 'industry': '企业',
                                   'job_keyword': '职位', 'publish_time': '招聘发布日期', 'salary': '月薪',
                                   'scale': '规模', 'technology_keyword': '技术关键词', 'treatment': '待遇'}, inplace=True)
        self.lagou = self.lagou[self.lagou['城市'] != 'city']
        self.lagou['学历'] = self.lagou['学历'].apply(lambda x: '{}/{}'.format(x.split(' ')[1], x.split(' ')[3]))
        self.lagou['职位'] = self.lagou['职位'].apply(lambda x: (x.replace(' ', '').lower()))
        self.lagou['待遇'] = self.lagou['待遇'].apply(lambda x: re.sub(r'[、，； /]', ',', x).
                                                  replace('“', '').replace('”', ''))
        self.lagou.reset_index(inplace=True, drop=True)
        self.lagou.to_csv('lagou_new.csv', index=False)

    def get_avg_salary(self, City: str, keyword: str):
        """
        获取每个城市每个职位的平均工资
        """
        try:
            city_condition = (City in str(city) for city in self.lagou['城市'])
            keyword_condition = (r'{}'.format(keyword) in str(position) for position in self.lagou['职位'])
            intersection_ = ((c and k) for c, k in zip(city_condition, keyword_condition))
            lagou_temp = self.lagou.loc[intersection_, '月薪']  # 选取在某个城市从事某个职位开发的交集
            total_salary = (salary.replace('K', '').replace('k', '').split('-') for salary in
                            lagou_temp if
                            len(salary.replace('K', '').replace('k', '').split('-')) == 2)  # 分出每个职位的最少月薪和最多月薪
            min_total = 0  # 最低总月薪
            max_total = 0  # 最高总月薪
            for each_salary in total_salary:  # 遍历 总月薪元祖
                min_total += int(each_salary[0])
                max_total += int(each_salary[1])
            min_total_avg = min_total / len(lagou_temp)
            max_total_avg = max_total / len(lagou_temp)
            del intersection_, total_salary, lagou_temp, city_condition, keyword_condition
            return '%.2f' % min_total_avg, '%.2f' % max_total_avg  # 保留两位小数
        except:
            return 'error:查询不到，城市{}:职位{}'.format(City, keyword)

    def get_experienced(self) -> list:
        """
        获取每个职位的学历和经验要求排名
        """
        IO = os.path.join(self.BASE_DIR, 'static/file/experienced.json')
        # IO = self.BASE_URL.replace('\\', '/') + '/static/file/experienced.json'
        # IO = 'static/file/experienced.json'
        experienced_file = Path(IO)
        if experienced_file.is_file():
            with open(IO, 'r', encoding='utf8') as experienced:
                result = json.load(experienced)
            return result['new_education']
        else:
            lagous = self.lagou
            new_education = sorted(Counter(lagous['学历']).items(), key=itemgetter(1),
                                   reverse=True)  # 提取元素，不像lambda会返回一个修改后的数,逆序输出
            dict_ = {
                'new_education': new_education
            }
            with open(IO, 'w', encoding='utf8') as experienced:
                json.dump(dict_, experienced)
            return new_education

    def get_scale(self) -> tuple:
        """
        获取应用领域排名
        """
        IO = os.path.join(self.BASE_DIR, 'static/file/scales.json').replace('\\', '/')
        # IO = 'static/file/experienced.json'
        scale_file = Path(IO)
        if scale_file.is_file():
            with open(IO, 'r', encoding='utf8') as scale:
                result = json.load(scale)
            return result['domain'], result['financing'], result['scale']
        else:
            temps = [scale.replace('/', '').split(' ') for scale in self.lagou['规模']]
            domain = []  # 应用领域
            financing = []  # 融资
            scale = []  # 规模
            for temp in temps:
                domain.append(temp[0])
                financing.append(temp[2])
                scale.append(temp[4])
            domain_temps = [i.replace('、', ',').split(',') for i in domain]  # 清理domain应用领域
            domain.clear()  # 清空数据
            for domain_temp in domain_temps:
                for i in range(len(domain_temp)):
                    domain.append(domain_temp[i])
            # domain_rank = sorted(Counter(domain).items(), key=itemgetter(1), reverse=True)  # 转为domain列表
            # financing_rank = sorted(Counter(financing).items(), key=itemgetter(1), reverse=True)  # 转为domain列表
            # scale_rank = sorted(Counter(scale).items(), key=itemgetter(1), reverse=True)  # 转为scale列表
            domain_rank = Counter(domain)  # 转为domain字典
            financing_rank = Counter(financing)  # 转为domain字典
            scale_rank = Counter(scale)  # 转为scale字典
            dict_ = {
                'domain': domain_rank,
                'financing': financing_rank,
                'scale': scale_rank,
            }
            del temps, domain, financing, scale  # 释放对象
            with open(IO, 'w', encoding='utf8') as scale:
                json.dump(dict_, scale)
            return domain_rank, financing_rank, scale_rank

    def get_details_salary(self):
        """注意传递参数要新生成一个副本，否则可能导致修改原有的对象"""
        global keyword, city
        salary = {}
        IO = os.path.join(self.BASE_DIR, 'static/file/salary.json').replace('\\', '/')
        # IO = 'static/file/experienced.json'
        salary_file = Path(IO)
        if salary_file.is_file():
            with open(IO, 'r', encoding='utf8') as salary:
                result = json.load(salary)
            return result
        else:
            try:
                for keyword in self.KEYWORDS:
                    context = []
                    for city in self.CITY_NAME:
                        min_total_avg, max_total_avg = self.get_avg_salary(city, keyword)
                        context.append({
                            '城市': city,
                            '平均最低月薪': min_total_avg + 'k',
                            '平均最高月薪': max_total_avg + 'k',
                        })
                    salary[keyword] = context
                    del context
                with open(IO, 'w', encoding='utf8') as salary_f:
                    json.dump(salary, salary_f)
                return salary
            except:
                return 'error:{}{}'.format(city, keyword)

    def get_treatment(self) -> list:
        """
        获取待遇排名
        :return: 待遇排名
        """
        IO = os.path.join(self.BASE_DIR, 'static/file/treatment.json').replace('\\', '/')
        # IO = 'static/file/treatment.json'
        treatment_file = Path(IO)
        if treatment_file.is_file():
            with open(IO, 'r', encoding='utf8') as treatment:
                result = json.load(treatment)
            return result['treat_rank']
        else:
            lagous = self.lagou
            total_treat = [treat for treats in lagous['待遇'] for treat in str(treats).split(',')]
            treat_rank = sorted(Counter(total_treat).items(), key=itemgetter(1), reverse=True)
            del lagous
            dict_ = {
                'treat_rank': treat_rank
            }
            with open(IO, 'w', encoding='utf8') as treatment:
                json.dump(dict_, treatment)
            return treat_rank

    def get_city_job(self):
        """
        每个城市每个职业的数量
        """
        global City, keyword
        total_keywords = {}
        lagous = self.lagou
        try:
            for keyword in self.KEYWORDS:
                total_citys = {}
                for City in self.CITY_NAME:
                    city_condition = (City in str(city) for city in lagous['城市'])
                    keyword_condition = (r'{}'.format(keyword) in str(position).lower().replace(' ', '') for position in
                                         lagous['职位'])
                    intersection_ = ((c and k) for c, k in zip(city_condition, keyword_condition))
                    lagou_temp = lagous.loc[intersection_, :]
                    total_citys[City] = len(lagou_temp)
                total_keywords[keyword] = total_citys
                del total_citys
            return total_keywords
        except:
            return {'error:{}-{}'.format(City, keyword)}


def get_lagou_obj():
    """
    实例化
    :return: 返回拉钩实例
    """
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file = os.path.join(BASE_DIR, 'static/file/lagou_new.csv')
    lagou_obj = analysis_lagou(file)  # 构造实例，获取数据
    # lagou_obj.first_clean()  # 初步清理
    return lagou_obj


