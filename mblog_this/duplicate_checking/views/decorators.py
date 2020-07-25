from collections import Counter
import re
import functools



def get_content_regex(chinese=False):
    """自定以内容正则"""
    if chinese:
        pattern = r'[^\w\u4e00-\u9fff]+'  # 过滤正则表达式中非英中文字符和数字的符号
    else:
        pattern = r'[^\u4e00-\u9fff]+' # 过滤除汉字以外的一切字符
    return pattern


def aim_or_whole(choice=True):
    pattern = get_content_regex(False)

    def decorate(func):
        @functools.wraps(func)
        def inner(obj, row=None, whole=choice):
            # 因为别装饰函数在类中定义，所以inner需要额外一个参数作为类实例obj
            global dict_context
            if choice:
                message = '全体匹配'
                dict_context = func(obj, row, True)
                sums = 0
                for key, values in dict_context.items():
                    for value in values:
                        value = re.sub(pattern, '', value)
                        sums += len(value)
                return sums
            else:
                message = '主体匹配'
                pass  # 自定义choice = True时的情况

        return inner

    return decorate
