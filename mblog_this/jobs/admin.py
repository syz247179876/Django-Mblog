from django.contrib import admin
from .models.jobs_models import Jobs


# Register your models here.

class JobAdmin(admin.ModelAdmin):
    list_display = ('job_keyword', 'city', 'salary', 'industry', 'scale', 'treatment', 'publish_time')


admin.site.register(Jobs, JobAdmin)
