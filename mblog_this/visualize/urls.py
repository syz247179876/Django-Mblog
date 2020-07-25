from django.urls import path, include

from visualize.views import visual

app_name = 'visualize'
user_analysis = ([
                     # 不需要登录
                     path('data_analysis/id=成绩分析/', visual.data_analysis_score, name='data_analysis/id=成绩分析'),
                     path('data_analysis/id=进程调度算法/', visual.data_analysis_process, name='data_analysis/id=进程调度算法'),
                     path('data_analysis/id=自定义图表/', visual.get_any_pyecharts, name='data_analysis/id=自定义图表'),
                     path('data_analysis/id=拉勾网数据分析/', visual.data_analysis_lagou, name='data_analysis/id=拉勾网数据分析'),
                     path('data_analysis/id=拉勾网数据展示/', visual.data_display_lagou, name='data_analysis/id=拉勾网数据展示'),
                 ], 'user_analysis')

urlpatterns = [
    path('user_analysis/', include(user_analysis), name='user_analysis'),
]
