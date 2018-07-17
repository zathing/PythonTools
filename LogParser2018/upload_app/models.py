from django.db import models

# Create your models here.
from django.utils import timezone

class FileSimpleModel(models.Model):
    file_name = models.CharField(max_length=100, default='SupportTool')
    file_field = models.FileField(upload_to='upload/%Y%m%d', max_length=200, unique=True)
    file_time = models.DateTimeField(default=timezone.now)
    file_username = models.CharField(max_length=50, default='admin')
    report_download = models.CharField(max_length=200, default='NotReady')
    # 按 file_time 倒序排序，-表示倒序
    class Meta:
        ordering = ['-file_time']
    def __str__(self):
        return self.file_name
    def get_report_path(self):
        if self.report_download == 'NotReady':
            return self.report_download
        else:
            report_name = self.report_download.split('/')[-1].split('.')[0]
            report_time = self.report_download.split('/')[1]
            report_path = './static/'+ report_time + '/' + report_name + '/' + report_name + '.html'
            return report_path