
from notes.models.notes_models import Note
from haystack import indexes
from haystack.forms import SearchForm
from haystack.views import SearchView
import jieba
import jieba.posseg   # 词性标注
import jieba.analyse  # 关键词提取


class NoteIndex(indexes.SearchIndex, indexes.Indexable):
    """
    定义关于Note的haystack搜索引擎
    """
    # document 表示该字段主要用于关键字查询的字段
    # use_Template表示该字段将从模板中指明
    text = indexes.CharField(document=True, use_template=True)
    # model_attr表明该字段将有模型中字段指明
    title = indexes.CharField(model_attr='title')
    note_author = indexes.CharField(model_attr='note_author')

    def get_model(self):
        # 返回建立索引的模型类
        return Note

    def index_queryset(self, using=None):
        # 返回建立索引的数据查询集
        return self.get_model().note_.all()


class MySearch(SearchView):
    """自定义查询"""
    def extra_context(self):
        introduce = '欢迎来到云博，这里是文章搜索页面，您可以根据作者名，任意词语等进行搜索，' \
                    '将给予您尽可能最完整的搜索结果!'
        return {
            'introduce':introduce
        }






