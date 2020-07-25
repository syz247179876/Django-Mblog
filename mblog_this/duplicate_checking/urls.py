from django.urls import path
from duplicate_checking.views import upload_homework


app_name = 'duplicate_checking'


urlpatterns = [
    # path('upload-homework/', upload_homework.UploadHomework.as_view(), name='upload-homework'),
    path('upload-homework/', upload_homework.UploadFile.as_view(), name='upload-homework-folder')
]
