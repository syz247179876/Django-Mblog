import logging

import markdown
from django.shortcuts import render

from ..models.notes_models import Note, Note_criticism


def get_article(request, slug):
    """
    获取指定slug笔记
    :param request:
    :param slug: the url of slug
    :return:
    """
    # user = request.session.get('user', default='游客')
    user = request.user.username if request.user.is_authenticated else '游客'
    note = Note.note_.get(slug=slug, status='Published')
    note.note_contents = markdown.markdown(note.note_contents, extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.attr_list',
        'markdown.extensions.smarty',
        'markdown.extensions.codehilite',  # 语法高亮拓展
        'markdown.extensions.toc',  # 自动生成目录
    ], safe_mode=True)  # 修改notes.note_contents内容为html
    new_read_counts = note.read_counts + 1
    # note.read_counts += 1
    # note.save()  # 等笔记修改好，网站上线，启动save
    Note.note_.filter(slug=slug).update(read_counts=new_read_counts)
    # Note.note_.get(slug=slug).__dict__.update(read_counts=new_read_counts) 通过get的__dict__属性来修改数据，最后要save保存model对象
    criticism_plural = Note_criticism.Note_criticism_.filter(note_slug=note)  # 对应note的留言
    criticism_msgs = {}
    for criticism in criticism_plural:
        criticism_msgs[criticism.id] = {
            'criticism_author_name': criticism.criticism_author.user.username,
            'criticism_praise_counts': criticism.praise_counts,
            'criticism_tread_counts': criticism.tread_counts,
            'criticism_dates': criticism.dates,
            'criticism_content': criticism.criticism_content,
            'criticism_author_head_image':  '/media/{filename}'.format(filename=criticism.criticism_author.head_image),
            'note_reply': [],
        }
        for reply in criticism.note_reply.all():
            # 都是按顺序ordering排好的
            replys = {
                'reply_author_name': reply.reply_author.user.username,
                'reply_praise_counts': reply.praise_counts,
                'reply_tread_counts': reply.tread_counts,
                'reply_dates': reply.dates,
                'reply_content': reply.reply_content,
                'reply_author_head_name':  '/media/{filename}'.format(filename=reply.reply_author.head_image),
                'reply_id': reply.id,
            }
            criticism_msgs[criticism.id]['note_reply'].append(replys)

    context = {
        'note': note,
        'user': user,
        'criticism_msgs': criticism_msgs,
    }
    return render(request, 'Articles.html', context)
