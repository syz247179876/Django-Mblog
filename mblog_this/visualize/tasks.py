from visualize.views import echarts
from mblog import celery_app as app
from visualize.views.analysis import get_lagou_obj
from notes.models.notes_models import Note
from collections import Counter




@app.task
def get_bar_score_compare():
    result = echarts.Bar_score_compare().render_embed()  # render_embed返回渲染后的图像
    return result


@app.task
def get_data_analysis_process():
    result = echarts.set_process().render_embed()
    return result


@app.task
def get_data_analysis_lagou_education(education):
    result = echarts.set_lagou_education(education).render_embed()
    return result


@app.task
def get_data_analysis_lagou_domain(domain_rank):
    result = echarts.set_lagou_domain(domain_rank).render_embed()
    return result


@app.task
def get_data_analysis_lagou_scale(scale_rank):
    result = echarts.set_lagou_scale(scale_rank).render_embed()
    return result


@app.task
def get_data_analysis_lagou_financing(financing_rank):
    result = echarts.set_lagou_financing(financing_rank).render_embed()
    return result


@app.task
def get_data_analysis_lagou_salary(salary, citys, profession_names):
    result = echarts.set_lagou_salary(salary, citys, profession_names).render_embed()
    return result


@app.task
def get_data_analysis_lagou_cityjobs(city_job):
    pass


@app.task
def get_data_analysis_lagou_treatment(treatment):
    result = echarts.set_lagou_treatment(treatment).render_embed()
    return result


@app.task
def set_bar():
    """设置树状图"""
    result = echarts.hickey_bar().render_embed()
    return result


@app.task
def set_sunburst():
    """设置旭日图"""
    result = echarts.hickey_sunburst().render_embed()
    return result


@app.task
def set_wordcloud():
    """设置词云图"""
    result = echarts.hickey_wordcloud().render_embed()
    return result


@app.task
def set_pie():
    """设置饼状图"""
    result = echarts.hickey_pie().render_embed()
    return result


@app.task
def set_funnel():
    """设置漏斗图"""
    result = echarts.hickey_funnel().render_embed()
    return result


@app.task
def set_liquid():
    """设置水球图"""
    result = echarts.hickey_liquid().render_embed()
    return result


@app.task
def set_gauge():
    """设置仪表盘"""
    pass


@app.task
def set_effect_scatter():
    """设置涟漪散点特效图"""
    result = echarts.hickey_effect_scatter().render_embed()
    return result


@app.task
def set_line():
    """设置折线图"""
    pass


@app.task
def set_pictorial_bar():
    """设置象形图"""
    pass


@app.task
def set_scatter():
    """设置散点图"""
    pass


@app.task
def set_china_map():
    """设置中国地图"""
    result = echarts.hickey_geo().render_embed()
    return result


@app.task
def update_daily_note():
    """日更笔记统计图"""
    notes = Note.note_.all()
    date = [note.publish_date.strftime('%Y-%m-%d') for note in notes]
    counter = Counter(date)
    data = [(date,counts) for date,counts in counter.items()]
    result = echarts.set_my_calendar(data).render_embed()
    return result

@app.task
def get_lagou_education():
    """
    平均经验学历任务
    :return:平均经验学历,应用领域，融资等级，公司规模
    """
    lagou = get_lagou_obj()
    new_education = lagou.get_experienced()  # 获取各职业学历经验要求，排序
    return new_education


@app.task
def get_lagou_scale():
    """
    应用领域，融资等级，公司规模任务
    :return:,应用领域，融资等级，公司规模
    """
    lagou = get_lagou_obj()
    domain_rank, financing_rank, scale_rank = lagou.get_scale()
    return domain_rank, financing_rank, scale_rank


@app.task
def get_lagou_salary():
    """
    最低最高平均工资
    :return: 最低最高平均工资任务
    """
    lagou = get_lagou_obj()
    salary = lagou.get_details_salary()
    citys = lagou.CITY_NAME
    profession_names = lagou.KEYWORDS
    return salary, citys, profession_names


@app.task
def get_lagou_city_job():
    """
    每个城市每个职业的数量
    :return:每个城市每个职业的数量
    """
    lagou = get_lagou_obj()
    city_job = lagou.get_city_job()
    return city_job


@app.task
def get_lagou_treatment():
    """
    所有企业的待遇
    :param lagou_obj:拉钩实例
    :return:待遇相同数量列表
    """
    lagou = get_lagou_obj()
    treatment = lagou.get_treatment()
    return treatment



