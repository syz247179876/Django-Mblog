from django.shortcuts import render, redirect
from django.urls import reverse

from rest_framework import serializers
from notes.models.notes_models import Note


class NoteSearchSerialize(serializers.ModelSerializer):
    # 获取外键的使用
    note_author = serializers.CharField(source='note_author.username', read_only=True)

    class Meta:
        model = Note
        fields = ('title', 'note_author', 'type', 'key_word')


def get_notes(request):
    """
    返回全局搜索
    :param request:
    :return:
    """
    return render(request, 'search.html')
