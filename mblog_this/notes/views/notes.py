from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render
from notes.models import notes_models


'''
def display_article(type_):
    """markdown修饰"""
    notes = notes_models.Note.note_.filter(slug__icontains=type_)
    for note in notes:
        note.note_contents = markdown(note.note_contents, extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
        ], safe_mode=True)
    return notes
'''


def get_article_counts() -> int:
    """
    获取当前已写的笔记总数量
    :return:
    """
    pass

'''
def get_notes(request, type_):
    """
    获取Python中type类型的文章
    :param type_:
    :param request:Request请求对象
    :return:对应序号的文章内容
    """
    # user = request.session.get('user', default='游客')
    user = request.user.username if request.user.is_authenticated else '游客'
    notes = notes_models.Note.note_.filter(type__iexact=type_, status='Published')
    return render(request, 'notes.html', locals())
'''


def get_notes(request, type_, page_number):
    """
    获取Python中type类型的文章,需要分页
    :param type_:文章类型
    :param request:Request请求对象
    :return:对应序号的文章内容
    """
    # user = request.session.get('user', default='游客')
    user = request.user.username if request.user.is_authenticated else '游客'
    try:
        number = page_number  # 获取前端请求的页数
    except Exception as e:
        number = 1
    data = {
        'user': user,
        'type': type_,
    }
    notes = notes_models.Note.note_.filter(type=type_, status='Published')
    try:
        # 初始化分页器列表，每页5篇，当第一页没有文章的时候，要求其自定义处理异常
        paginator = Paginator(notes, 5, allow_empty_first_page=False)
        # 通过page()来创建Page对象,前端的模板语言也可以会调用函数
        notes = paginator.page(number=number)
        data['notes'] = notes
        return render(request, 'notes.html', data)
    except EmptyPage:
        data['error'] = '当前类别没有笔记，如果您想要加盟云博的话,为此页增添技术文章，共同学习进步的话，请注册成为本站的vip，一起记录学习的心得'
        return render(request, 'notes.html', data)
