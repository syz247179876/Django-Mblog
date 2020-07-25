from collections import Counter
from mblog import celery_app as app
import logging

duplicate_log= logging.getLogger('duplicate_')

@app.task
def write_down(filename,file):
    try:
        with open(filename, 'wb') as homework_F:
            # chunks以块的形式将图片大文件写入文件中，如果文件过大，会占用系统内存，导致变慢，因此分块写更好
            for i in file.chunks():
                homework_F.write(i)
    except Exception as e:
        duplicate_log.error(str(e))
