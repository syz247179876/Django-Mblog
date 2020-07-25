from collections import Counter

from notes.models.notes_models import Note
from visualize.views import echarts
from django.core.mail import send_mail
from mblog import celery_app as app
from mblog.settings import EMAIL_HOST_USER
import random
import string

import logging

common_log = logging.getLogger('django')

def set_verification_code() -> str:
    """自定义验证码"""
    reset_password = ''
    random.seed(random.randint(1, 100))
    for i in range(6):
        m = random.randrange(1, 9)
        if i == m:
            reset_password += str(m)
        else:
            reset_password += random.choice(string.ascii_uppercase)
    return reset_password


@app.task
def send_verification(title, content, user_email):
    """
    发送邮件
    :param title:标题
    :param content:内容
    :param user_email:对方邮箱
    :return:按道理说参数和返回值无类型要求
    """
    # fail_Silently为False表示会出错会报异常，方便捕捉
    send_mail(title, content, EMAIL_HOST_USER, [user_email], fail_silently=False)


@app.task
def get_word_cloud():
    """笔记类型统计"""
    notes = Note.note_.all()
    notes_type = (note.type for note in notes)
    counter = Counter(notes_type)
    data = [(note_type, counts) for note_type, counts in counter.items()]
    result = echarts.set_wordcloud(data).render_embed()
    return result

@app.task
def update_daily_note():
    """日更笔记统计"""
    notes = Note.note_.all()
    date = [note.publish_date.strftime('%Y-%m-%d') for note in notes]
    counter = Counter(date)
    data = [(date, counts) for date, counts in counter.items()]
    result = echarts.set_my_calendar(data).render_embed()
    return result


@app.task
def tests_Periodic():
    common_log.info('云中最帅')
