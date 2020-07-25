import json
import logging
from django.db.models import Q
from django.http import JsonResponse
from requests import Response
from rest_framework.views import APIView
from ..models.visualize_models import lagou

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated


def lagou_table_api(request):
    global results, max_salary, min_salary

    lagou_json_filename = 'static/file/lagou_json.json'
    page = int(request.GET.get('page', default=1))  # get请求前端table发来的参数
    limit = int(request.GET.get('limit', default=10))
    education = request.GET.get('education')
    city = request.GET.get('city')
    salary = request.GET.get('salary')
    experience = request.GET.get('experience')
    keyword = request.GET.get('keyword')
    # 不为None或 ''
    if not any([education, city, salary, experience, keyword]) or (
            education == '' and city == '' and salary == '' and experience == '' and keyword == ''):
        with open(lagou_json_filename, encoding='utf-8') as f:
            lagou_jsonData = json.load(f)
            datas = {  # 和with平级
                'code': 0,
                'msg': "",
                'count': len(lagou_jsonData),
                'data': lagou_jsonData[((page - 1) * limit) + 1:(page * limit)]
            }
        return JsonResponse(datas)

    else:
        if experience == '0':
            experience = '应届毕业生'
        elif experience == '1-':
            experience = '1年以下'
        elif experience == '10+':
            experience = '10年以上'
        elif experience == '666':
            experience = '经验不限'
        job_keywords = keyword.split(',')[:-1]
        if len(job_keywords) != 0:
            temp_job = ["Q(job__icontains='{}')".format(job) for job in job_keywords]
            job_filter = '|'.join(temp_job)
        else:
            job_filter = "Q(job__icontains='')"
        data_lagou = []
        # 此时education为本科，city为上海,月薪为10k-15k,经验要求1年以下
        results = lagou.lagou_.filter(Q(education__contains=education) & Q(education__contains=experience),
                                      # reduce(lambda x, y: Q(job__icontains=x) | Q(job__icontains=y), job_keywords),
                                      eval(job_filter),
                                      # Q对象一定要放在关键词查询的前面
                                      city__contains=city)
        if salary != '':
            salary = salary.split('-')
            min_salary = int(salary[0])
            max_salary = int(salary[1])
            for result in results:
                temp_salary = result.salary.replace('k', '').replace('K', '').split('-')
                # 长沙的java简直有毒，草！
                if len(temp_salary) == 2 and 'k' not in temp_salary[1] and 'k' not in temp_salary[0] and \
                        max_salary < int(temp_salary[1]) and min_salary > int(temp_salary[0]):
                    data_dict = {
                        'index': result.id,
                        'city': result.city,
                        'education': result.education,
                        'industry': result.industry,
                        'job_keyword': result.job,
                        'publish_time': result.recruit_name,
                        'salary': result.salary,
                        'scale': result.scale,
                        'technology_keyword': result.technique_key,
                        'treatment': result.treatment,
                    }
                    data_lagou.append(data_dict)
                    del data_dict
        else:
            for result in results:
                data_dict = {
                    'index': result.id,
                    'city': result.city,
                    'education': result.education,
                    'industry': result.industry,
                    'job_keyword': result.job,
                    'publish_time': result.recruit_name,
                    'salary': result.salary,
                    'scale': result.scale,
                    'technology_keyword': result.technique_key,
                    'treatment': result.treatment,
                }
                data_lagou.append(data_dict)
                del data_dict
        datas_modify = {  # 仍然是全局的
            'code': 0,
            'msg': "",
            'count': len(data_lagou),  # 总数
            'data': data_lagou[((page - 1) * limit) + 1:(page * limit)]
        }
        return JsonResponse(datas_modify)

'''
class test(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {
            'user': request.user,
            'auth': request.auth
        }
        return Response(content)
'''
