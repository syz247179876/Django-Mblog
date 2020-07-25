import json
from visualize import tasks
from django.shortcuts import render

# from mblog.celery import app
from django.views.decorators.cache import cache_page




def data_analysis_score(request):
    score_data = tasks.get_bar_score_compare.delay().get()
    visualize = True
    # user = request.session.get('user', default='游客')
    user = request.user.username if request.user.is_authenticated else '游客'
    title = '大二上学期系里排名第4名'
    datas = {
        'user': user,
        'data': score_data,
        'visualize': visualize,
        'title': title,
        'category': 'score_compare',
    }
    return render(request, 'visualization.html', datas)


def data_analysis_process(request):
    process_data = tasks.get_data_analysis_process.delay().get()
    visualize = True
    # user = request.session.get('user', default='游客')
    user = request.user.username if request.user.is_authenticated else '游客'
    title = '操作系统进程调度算法性能比较'
    datas = {
        'user': user,
        'data': process_data,
        'visualize': visualize,
        'title': title,
        'category': 'process_scheduling',

    }
    return render(request, 'visualization.html', datas)

# @cache_page(60*30*24)
def get_any_pyecharts(request):
    # user = request.session.get('user', default='游客')
    user = request.user.username if request.user.is_authenticated else '游客'
    bar = tasks.set_bar.delay().get()
    sunburst = tasks.set_sunburst.delay().get()
    wordcloud = tasks.set_wordcloud.delay().get()
    pie = tasks.set_pie.delay().get()
    funnel = tasks.set_funnel.delay().get()
    liquid = tasks.set_liquid.delay().get()
    effect_scatter = tasks.set_effect_scatter.delay().get()
    china_map = tasks.set_china_map.delay().get()
    datas = {
        'user': user,
        'bar': bar,
        'sunburst': sunburst,
        'wordcloud': wordcloud,
        'pie': pie,
        'funnel': funnel,
        'liquid': liquid,
        'effect_scatter': effect_scatter,
        'china_map': china_map,
        'category': 'pyecharts接口',
        'title': 'pyecharts接口',
        'visualize': True
    }
    return render(request, 'any_pyecharts.html', datas)


def each_pos_salary(salary, profession_name):
    """
    进一步对salary提取数据优化,获取不同职位每个城市的月薪情况
    :param profession_name:城市
    :param salary:月薪{position:[{city}{}{}{}{}],position:[{}{}{}{}{}]}格式
    :return:
    """
    lowest_avg_salary = []
    highest_avg_salary = []
    citys = salary[profession_name]
    for city in citys:
        lowest_avg_salary.append(city['平均最低月薪'])
        highest_avg_salary.append(city['平均最高月薪'])
    return lowest_avg_salary, highest_avg_salary

@cache_page(60*24*60*30)
def data_analysis_lagou(request):
    # user = request.session.get('user', default='游客')
    user = request.user.username if request.user.is_authenticated else '游客'
    lagou_education = tasks.get_lagou_education.delay().get()  # 获取经验门槛列表     # celery执行任务接收的参数必须是json序列化的，传的参数里面有一些python对象，不能进行json的序列化，要么换一下参数类型，或者把传递方式换成pickle
    domain_rank, financing_rank, scale_rank = tasks.get_lagou_scale.delay().get()  # 获取应用领域，规模，融资
    # city_job = get_lagou_city_job.delay().get()  # 获取每个城市每个职业的数量
    treatments = tasks.get_lagou_treatment.delay().get()
    # 这里可能存在一个任务调度优先级的问题，如果出错可以尝试使用yield from
    education = tasks.get_data_analysis_lagou_education.delay(lagou_education).get()
    domain = tasks.get_data_analysis_lagou_domain.delay(domain_rank).get()
    financing = tasks.get_data_analysis_lagou_financing.delay(financing_rank).get()
    scale = tasks.get_data_analysis_lagou_scale.delay(scale_rank).get()
    # cityjobs = tasks.get_data_analysis_lagou_cityjobs.delay(city_job).get()
    treatment = tasks.get_data_analysis_lagou_treatment.delay(treatments).get()
    visualize = True
    datas = {
        'user': user,
        'title': '拉勾网数据分析大全---1月份',
        'education': education,
        'domain': domain,
        'financing': financing,
        'scale': scale,
        # 'cityjobs': cityjobs,
        'visualize': visualize,
        'treatment': treatment,
        'category': 'lagou_analysis',
    }
    return render(request, 'visualization.html', datas)

@cache_page(60*24*60*30)
def data_display_lagou(request):
    """
    拉勾网数据数据table展示
    :param request:request对象
    :return:
    """
    salary, citys, profession_names = tasks.get_lagou_salary.delay().get()  # 获取月薪，城市，职业
    salarys = tasks.get_data_analysis_lagou_salary.delay(salary, citys, profession_names).get()
    # user = request.session.get('user', default='游客')
    user = request.user.username if request.user.is_authenticated else '游客'
    datas = {
        'user': user,
        'title': '拉勾网数据展示',
        'category': 'lagou_display',
        'visualize': True,
        'salary': salarys,
    }
    return render(request, 'visualization.html', datas)

