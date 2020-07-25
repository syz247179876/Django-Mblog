import random
from pyecharts.charts import *
from pyecharts.globals import SymbolType
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from datetime import datetime, date, time, timedelta
from jinja2 import Environment, FileSystemLoader
from pyecharts.globals import CurrentConfig
from pyecharts.faker import Faker
from visualize.views import analysis
from visualize.views.visual import each_pos_salary

CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./visualize/charts_templates"))


def syz_mark():
    """私人标记"""
    graphic_opts = [
        opts.GraphicGroup(
            graphic_item=opts.GraphicItem(
                rotation=JsCode("Math.PI / 4"),
                bounding="raw",
                right=80,
                bottom=80,
                z=100,
            ),
            children=[
                opts.GraphicRect(
                    graphic_item=opts.GraphicItem(
                        left="center", top="center", z=100
                    ),
                    graphic_shape_opts=opts.GraphicShapeOpts(
                        width=400, height=50
                    ),
                    graphic_basicstyle_opts=opts.GraphicBasicStyleOpts(
                        fill="rgba(0,0,0,0.3)"
                    ),
                ),
                opts.GraphicText(
                    graphic_item=opts.GraphicItem(
                        left="center", top="center", z=100
                    ),
                    graphic_textstyle_opts=opts.GraphicTextStyleOpts(
                        text="云博",
                        font="bold 26px Microsoft YaHei",
                        graphic_basicstyle_opts=opts.GraphicBasicStyleOpts(
                            fill="#fff"
                        ),
                    ),
                ),
            ],
        )
    ]
    return graphic_opts


def Bar_score_compare() -> Bar:
    """
    成绩比较图
    :return:Bar
    """
    compare_list = analysis.get_all_information()
    bar = (
        Bar(init_opts=opts.InitOpts(
            width='1000px',
            height='550px',
            animation_opts=opts.AnimationOpts
                (
                animation_delay=100,
            )
        )
        )
            .add_xaxis(compare_list['columns'])
            .add_yaxis(compare_list['first_name'], compare_list['first_score'],
                       itemstyle_opts={
                           'color': JsCode("""new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                                                                offset: 0,
                                                                color: 'red'
                                                            }, {
                                                                offset:1,
                                                                color: 'orange'
                                                            }], false)"""),
                           'barBorderRadius': [30, 30, 30, 30],
                           'shadowColor': 'rgb(0, 160, 200)',
                       },
                       )
            .add_yaxis(compare_list['my_name'], compare_list['my_score'],
                       itemstyle_opts={
                           'color': JsCode("""new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                                                                offset: 0,
                                                                color: 'yellow'
                                                            }, {
                                                                offset:1,
                                                                color: 'pink'
                                                            }], false)"""),
                           'barBorderRadius': [30, 30, 30, 30],
                           'shadowColor': 'rgb(0, 160, 200)',
                       },
                       )
            .extend_axis(yaxis=opts.AxisOpts(type_='value', name='成绩波动线', max_=100, min_=0,
                                             axislabel_opts=opts.LabelOpts(position='right',
                                                                           margin=12,
                                                                           formatter='{value}/分', )
                                             , ), )
            .set_global_opts(title_opts=opts.TitleOpts(title='成绩比较图',
                                                       subtitle='我和系里第一名',
                                                       title_textstyle_opts=opts.TextStyleOpts(color='green')),
                             # toolbox_opts=opts.ToolboxOpts(),
                             xaxis_opts=opts.AxisOpts(type_='category', name='综合成绩',
                                                      axislabel_opts=opts.LabelOpts(rotate=70)),
                             yaxis_opts=opts.AxisOpts(type_='value',
                                                      name='分数',
                                                      max_=140,
                                                      axislabel_opts=opts.LabelOpts(formatter='{value}/分',
                                                                                    rotate=30),
                                                      ),
                             datazoom_opts=[opts.DataZoomOpts(type_='inside'),
                                            opts.DataZoomOpts(orient='vertical')],
                             graphic_opts=syz_mark(),
                             tooltip_opts=opts.TooltipOpts(trigger='axis', axis_pointer_type='cross')

                             )
            .set_series_opts(
            markpoint_opts=opts.MarkPointOpts(data=[
                opts.MarkPointItem(name='最大值', type_='min'),
                opts.MarkPointItem(name='最小值', type_='max'),
            ],
            ),
            label_opts=opts.LabelOpts(is_show=False)
        )
    )
    line = (
        Line()
            .add_xaxis(compare_list['columns'])
            .add_yaxis('成绩波动',
                       y_axis=compare_list['my_score'],
                       symbol='roundRect',
                       symbol_size=15,
                       yaxis_index=1,
                       linestyle_opts=opts.LineStyleOpts(color='blue', width=3, opacity=0.6, curve=2,
                                                         type_='dotted')
                       )
    )
    bar.overlap(line)
    return bar



def set_wordcloud(data) -> WordCloud:
    """词云图"""
    wordcloud = (
        WordCloud(init_opts=opts.InitOpts(width='800px', height='300px'))
            .add(
            series_name='人生苦短，我用Python',
            data_pair=data, shape='star',
            word_size_range=[20, 80],
            rotate_step=60,
        )
            .set_global_opts(title_opts=opts.TitleOpts(title='本站博客文章词云'))
    )
    return wordcloud


def set_my_calendar(data) -> Calendar:
    """日历图"""
    year = datetime.now().strftime('%Y')
    Begin = date(int(year), 1, 1)
    End = date(int(year), 12, 31)
    data = data
    calendar = (
        Calendar()
            .add('我的文章发布统计', yaxis_data=data,
                 calendar_opts=opts.CalendarOpts(range_=year,pos_left="10%",pos_right="8%",pos_top="15%"))
            .set_global_opts(
            title_opts=opts.TitleOpts(title='云博网站文章发布每日统计',pos_left="center"),
            legend_opts=opts.LegendOpts(is_show=False),
            visualmap_opts=opts.VisualMapOpts
                (
                min_=0,
                max_=10,
                orient='horizontal',
                is_piecewise=True,
                pos_top='center',
                pos_left="center",
            ),
        )
    )
    return calendar


def set_liquid() -> Liquid:
    """水球图"""
    weekdays = date.today().weekday()
    liquid_total = zip(range(7), [0.14, 0.28, 0.42, 0.56, 0.70, 0.84, 0.96],
                       ['red', 'orange', 'yellow', 'green', 'blue', 'pink', 'purple'])
    every_liquid = [(day, rate, color) for day, rate, color in liquid_total]
    today_rate = []
    today_color = ''
    for days in every_liquid:
        if weekdays == days[0]:
            today_rate.append(days[1])
            today_color = days[2]
            break
    liquid = (
        Liquid()
            .add("今日能量",
                 today_rate,
                 is_outline_show=False,
                 color=today_color,
                 shape='arrow')
            .set_global_opts(title_opts=opts.TitleOpts(title="今日能量"))
    )
    return liquid


def set_process() -> Bar:
    """
    进程调度比较图
    :return:
    """
    index = ['时间片轮转调度', '短进程优先调度', '非剥夺优先级调度']
    data = [217, 459, 324]
    bar = (
        Bar()
            .add_xaxis(index)
            .add_yaxis(series_name='三大调度算法', yaxis_data=data)
            .set_global_opts(title_opts=opts.TitleOpts(title='三大算法调度性能分析'),
                             xaxis_opts=opts.AxisOpts(type_='category', name='算法名称'),
                             yaxis_opts=opts.AxisOpts(type_='value', name='获胜次数',
                                                      axislabel_opts=opts.LabelOpts(formatter='{value}/次')),
                             toolbox_opts=opts.ToolboxOpts(),
                             tooltip_opts=opts.TooltipOpts(axis_pointer_type='cross')
                             )
            .set_series_opts(markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(name='最大值', type_='min'),
                                                                     opts.MarkPointItem(name='最大值', type_='max')]),
                             itemstyle_opts={
                                 "normal": {
                                     "color": JsCode("""new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                                             offset: 0,
                                             color: 'rgba(0, 244, 255, 1)'
                                         }, {
                                             offset: 1,
                                             color: 'rgba(0, 77, 167, 1)'
                                         }], false)"""),
                                     "barBorderRadius": [30, 30, 30, 30],
                                     "shadowColor": 'rgb(0, 160, 221)',
                                 }}
                             )
    )
    return bar


def set_lagou_education(education):
    """
    绘制拉勾网经验学历要求图,采用象形图
    :return:
    """
    experienced = ['{}+{}'.format(i.split('/')[1], i.split('/')[0]).replace('经验', '') for i in
                   [e[0] for e in education]]
    counts = [i[1] for i in education]
    pictorialbar = (
        PictorialBar(init_opts=opts.InitOpts(width='700px', height='500px'))
            .add_xaxis(experienced)
            .add_yaxis("最新拉勾网20000+职位数据的学历经验门槛",
                       counts,
                       symbol=SymbolType.DIAMOND,
                       symbol_repeat=True,
                       symbol_repeat_direction='end',
                       is_symbol_clip=True,
                       color='#DEB887',
                       )
            .reversal_axis()  # 翻转
            .set_global_opts(title_opts=opts.TitleOpts(title='拉勾网30000+招聘的企业的工作经验+学历门槛'),
                             xaxis_opts=opts.AxisOpts(is_show=False),
                             yaxis_opts=opts.AxisOpts(axisline_opts=opts.AxisLineOpts(is_show=False),
                                                      axistick_opts=opts.AxisTickOpts(is_show=False),
                                                      axislabel_opts=opts.LabelOpts(margin=-2)
                                                      ),
                             legend_opts=opts.LegendOpts(pos_left='right')
                             )
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False,
                                                       position='right'),
                             markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(name='最大值',
                                                                                        type_='max',
                                                                                        # value_index=0,
                                                                                        ),
                                                                     opts.MarkPointItem(name='最小值',
                                                                                        type_='min',
                                                                                        ),
                                                                     ]
                                                               ),
                             )
    )
    return pictorialbar


def set_lagou_domain(domain_rank):
    """
    绘制拉勾网企业应用领域图，采用词云图
    :return:词云图对象
    """
    domain_words = []
    for key, value in domain_rank.items():
        domain_words.append((key, value))
    wordcloud = (
        WordCloud(init_opts=opts.InitOpts(width='800px', height='600px'))
            .add(
            series_name='应用领域',
            data_pair=domain_words,
            shape='pentagon',
            word_size_range=[20, 100],
            rotate_step=60,
        )
            .set_global_opts(title_opts=opts.TitleOpts(title='拉勾网30000+招聘的企业的技术应用领域'))
    )
    return wordcloud


def set_lagou_financing(financing_rank):
    """
    绘制拉勾网企业融资图，采用倒漏斗图
    :param financing_rank:
    :return:漏斗图对象
    """
    # 可以用sorted直接将Counter转化为列表形式，里面嵌套字典
    data = [
        [key, value]
        for key, value in financing_rank.items()
    ]
    funnel = (
        Funnel(init_opts=opts.InitOpts(width='700px', height='500px'))
            .add('企业融资图', data_pair=data, gap=20)
            .set_global_opts(
            title_opts=opts.TitleOpts(title='拉勾网30000+招聘的企业的技术融资情况'),
            toolbox_opts=opts.ToolboxOpts(is_show=False),
            legend_opts=opts.LegendOpts(type_='scroll', orient='vertical',
                                        align='right', legend_icon='circle',
                                        pos_left=1, pos_top=150,
                                        textstyle_opts=opts.TextStyleOpts(font_family='楷体',
                                                                          font_size=16))
        )
    )
    return funnel


def set_lagou_scale(scale_rank):
    """
    绘制拉勾网企业规模图，采用漏斗图
    :param scale_rank:Counter类型的scale字典rank
    :return:漏斗图对象
    """
    data = [
        [key, value]
        for key, value in scale_rank.items() if key != ''
    ]
    funnel = (
        Funnel(init_opts=opts.InitOpts(width='650px', height='450px'))
            .add('企业融资图', data_pair=data, gap=5)
            .set_global_opts(
            title_opts=opts.TitleOpts(title='拉勾网30000+招聘的企业的人员规模', pos_left='right'),
            toolbox_opts=opts.ToolboxOpts(is_show=False),
            legend_opts=opts.LegendOpts(type_='scroll', orient='vertical',
                                        align='right', legend_icon='arrow',
                                        pos_left=1, pos_top=150,
                                        textstyle_opts=opts.TextStyleOpts(font_size=14, font_family='宋体'))

        )
    )
    return funnel


def set_lagou_treatment(treatment):
    """
    绘制拉勾网企业待遇图，采用词云图
    :param treatment:列表类型，里面嵌套元组
    :return:词云图对象
    """
    wordcloud = (
        WordCloud(init_opts=opts.InitOpts(width='700px', height='500px'))
            .add(
            series_name='应用领域',
            data_pair=treatment,
            shape='star',
            word_size_range=[20, 100],
            # rotate_step=60,
        )
            .set_global_opts(title_opts=opts.TitleOpts(title='拉勾网30000+招聘的企业的技术应用领域'))
    )
    return wordcloud


def set_lagou_salary(salary, citys, profession_names):
    """
    绘制拉勾网月薪图，横轴为城市，标题为各个职业，纵轴为月薪,采用树状图
    :param salary:工资
    :param profession_names:职位名称列表
    :param citys:城市
    :return:tab选项卡
    """
    '''
    citys = list(citys)
    salary_expecial = each_pos_salary(salary, 'java')
    common_bar = set_common_salary(citys, salary_expecial, 'java')
    return common_bar
    '''

    tab = Tab()  # 选项卡
    citys = list(citys)
    for profession_name in ('python', 'java', 'c#', 'c++', 'web'):
        salary_expecial = each_pos_salary(salary, profession_name)
        common_bar = set_common_salary(citys, salary_expecial, profession_name)
        tab.add(common_bar, profession_name)
    return tab


def set_common_salary(citys, position, profession_name):
    """
    通用salary柱状图显示
    :param citys:城市
    :param profession_name:职业名称
    :param position:单个职业
    :return:bar对象
    """
    data_min = [i.replace('k', '') for i in position[0]]
    data_max = [i.replace('k', '') for i in position[1]]
    bar_common = (
        Bar(init_opts=opts.InitOpts(width='700px', height='500px'))
            .add_xaxis(citys)
            .add_yaxis("{}平均最低月薪".format(profession_name), data_min, stack=1)
            .add_yaxis("{}平均最高月薪".format(profession_name), data_max, stack=1)
            .set_global_opts(
            title_opts=opts.TitleOpts(title="拉勾网30000+招聘的企业的{}月薪详情比较".format(profession_name),
                                      subtitle=profession_name),
            legend_opts=opts.LegendOpts(pos_right=10),
            datazoom_opts=[opts.DataZoomOpts()],
            xaxis_opts=opts.AxisOpts(type_='category', name='城市'),
            yaxis_opts=opts.AxisOpts(type_='value', name='平均月薪', axislabel_opts=opts.LabelOpts(formatter='{value}/k')),
        )
            .set_series_opts(
            label_opts=opts.LabelOpts()
        )
    )
    return bar_common


# 以下是接口绘图
def hickey_funnel() -> Funnel:
    data = [
        [i, random.randint(100, 500)]
        for i in ['小米', '华为', '苹果', 'OPPO', 'Vivo', '三星', '魅族']
    ]
    funnel = (
        Funnel()
            .add('商品数量', data_pair=data)
            .set_global_opts(
            title_opts=opts.TitleOpts(title='漏斗图接口'),
            toolbox_opts=opts.ToolboxOpts(is_show=True),
        )
    )
    return funnel


def hickey_bar() -> Bar:
    bar = (
        Bar()
            .add_xaxis(Faker.animal)
            .add_yaxis('2019年', Faker.values())
            .add_yaxis('2020年', Faker.values())
            .set_global_opts(title_opts=opts.TitleOpts(title='树状图接口'),
                             toolbox_opts=opts.ToolboxOpts(is_show=True),
                             )

    )
    return bar


def hickey_liquid() -> Liquid:
    liquid = (
        Liquid()
            .add("今日能量",
                 [0.1, 0.3, 0.5],
                 is_outline_show=False,
                 color=['yellow'],
                 shape='arrow')
            .set_global_opts(title_opts=opts.TitleOpts(title="水球图接口"),
                             toolbox_opts=opts.ToolboxOpts(is_show=True),
                             )
    )
    return liquid


def hickey_pie() -> Pie:
    data = [
        [i, random.randint(100, 500)]
        for i in ['小米', '华为', '苹果', 'OPPO', 'Vivo', '三星', '魅族']
    ]
    pie = (

        Pie()
            .add('手机销售比例', data, radius=['30%', '75%'], rosetype='area')
            .set_global_opts(title_opts=opts.TitleOpts(title='饼状图接口'),
                             legend_opts=opts.LegendOpts(orient='vertical',
                                                         pos_left='15%',
                                                         pos_top='18%'),
                             toolbox_opts=opts.ToolboxOpts(is_show=True),
                             )
            .set_series_opts(label_opts=opts.LabelOpts(color='auto'))

    )
    return pie


def hickey_sunburst() -> Sunburst:
    data = [
        opts.SunburstItem(
            name='贾演',
            value=90,
            children=[
                opts.SunburstItem(
                    name='贾代化',
                    value=85,
                    children=[
                        opts.SunburstItem(
                            name='贾敬',
                            value=75,
                            children=[
                                opts.SunburstItem(
                                    name='贾珍',
                                    value=45,
                                    children=[
                                        opts.SunburstItem(
                                            name='贾蓉',
                                            value=20,
                                        ),
                                        opts.SunburstItem(
                                            name='秦可卿(外)',
                                            value=5,
                                        ),
                                    ],
                                ),
                                opts.SunburstItem(
                                    name='尤氏（继配）',
                                    value=39,
                                    children=[
                                        opts.SunburstItem(
                                            name='尤二姐',
                                            value=17,
                                        ),
                                        opts.SunburstItem(
                                            name='尤三姐',
                                            value=15,
                                        ),
                                    ],
                                ),
                                opts.SunburstItem(
                                    name='贾惜春',
                                    value=35,
                                ),
                            ],

                        ),
                    ],
                ),
            ],
        ),
    ]
    sunburst = (
        Sunburst()
            .add(
            series_name='红楼梦',
            data_pair=data,
            radius=['10%', '70%'], )
            .set_global_opts(title_opts=opts.TitleOpts(title='红楼梦谱系图'),
                             toolbox_opts=opts.ToolboxOpts(is_show=True),
                             )
        # .set_series_opts(label_opts=opts.LabelOpts(formatter={'b'}))
    )
    return sunburst


def hickey_wordcloud() -> WordCloud:
    wordcloud = (
        WordCloud()
            .add(
            series_name='人生苦短，我用Python',
            data_pair=set_word(), shape='star',
            word_size_range=[20, 100],
            rotate_step=60,
        )
            .set_global_opts(title_opts=opts.TitleOpts(title='词云图接口'),
                             toolbox_opts=opts.ToolboxOpts(is_show=True))
    )
    return wordcloud


def hickey_effect_scatter() -> EffectScatter:
    effectscatter = (
        EffectScatter()
            .add_xaxis(Faker.clothes)
            .add_yaxis(series_name='销售量',
                       y_axis=Faker.values(),
                       symbol=SymbolType.ARROW,
                       symbol_size=15,
                       )
            .set_global_opts(title_opts=opts.TitleOpts(title='涟漪散点图接口'),
                             xaxis_opts=opts.AxisOpts(splitline_opts=opts.AxisLineOpts(is_show=True), ),
                             yaxis_opts=opts.AxisOpts(splitline_opts=opts.AxisLineOpts(is_show=True), ),
                             visualmap_opts=opts.VisualMapOpts(type_='color', min_=20, max_=150,
                                                               range_text=['high', 'low'],
                                                               is_piecewise=False),
                             toolbox_opts=opts.ToolboxOpts(is_show=True),
                             )
    )
    return effectscatter


def hickey_geo() -> Geo:
    geo = (
        Geo()
            .add_schema(maptype="china")
            .add("geo", [z for z in zip(Faker.provinces, Faker.values())]
                 , type_='effectScatter',
                 color='blue')
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
            visualmap_opts=opts.VisualMapOpts(is_piecewise=False),
            title_opts=opts.TitleOpts(title="Geo地理图接口"),
            toolbox_opts=opts.ToolboxOpts(is_show=True),
        )
    )
    return geo
