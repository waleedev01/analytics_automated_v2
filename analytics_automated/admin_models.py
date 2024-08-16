from django.db import models

class DownloadCWLModel(models.Model):
    class Meta:
        managed = False
        verbose_name_plural = 'Download CWL'
        app_label = 'analytics_automated'

class UploadCWLModel(models.Model):
    class Meta:
        managed = False
        verbose_name_plural = 'Upload CWL'
        app_label = 'analytics_automated'