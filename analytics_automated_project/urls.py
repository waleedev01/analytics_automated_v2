"""analytics_automated_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf import settings
from django.conf.urls import include
from django.urls import re_path as url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views

from rest_framework.urlpatterns import format_suffix_patterns

from analytics_automated import api
from analytics_automated.views import * 

urlpatterns = [
     url(r'^admin/', include('smuggler.urls')),
     url(r'^admin/', admin.site.urls),
     url(r'^analytics_automated/', include('analytics_automated.urls')),
     url(r'^analytics_automated/submission/$',
         api.SubmissionDetails.as_view(),
         name="submission"),
     url(r'^analytics_automated/submission/single/'
         '(?P<UUID>.{8}-.{4}-.{4}-.{4}-.{12})$',
         api.SubmissionDetails.as_view(),
         name="submissionDetail"),
     url(r'^analytics_automated/submission/'
         '(?P<UUID>.{8}-.{4}-.{4}-.{4}-.{12})$',
         api.BatchDetails.as_view(),
         name="batchDetail"),
     url(r'^analytics_automated/job/$', api.JobList.as_view(), name="job"),
     url(r'^analytics_automated/job/(?P<name>.+)',
         api.JobDetail.as_view(), name="jobDetail"),
     url(r'^analytics_automated/endpoints/$',
         api.Endpoints.as_view(), name="endpoints"),
     url(r'^analytics_automated/jobtimes/$',
         api.JobTimes.as_view(), name="jobtimes"),
     url(r'^analytics_automated/uploadcwl/$',
         api.CWLUploadView.as_view(), name="uploadcwl"),  # Existing CWL upload pattern
     url(r'^analytics_automated/admin_upload_cwl/$', UploadCWLView, name="admin_upload_cwl"),  # New view for the admin CWL upload
     url(r'^analytics_automated/admin_download_cwl/$', DownloadCWLView, name="admin_download_cwl"),  # New view for the admin CWL download
     url(r'^analytics_automated/dynamic-visualize/(?P<submission_name>.+)$',
         DashboardView.as_view(), name='dynamic_visualize'),
     url(r'^analytics_automated/static-visualize/$',
         StaticWorkflowGraphView.as_view(), name='static_visualize'),
     url(r'^analytics_automated/api/task-states/(?P<submission_name>.+)',
         api.TaskStatesView.as_view(), name='task_states'),   
     url(r'^login/$', auth_views.LoginView.as_view(), name='login'),
     url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html'])

# UNDERNEATH your urlpatterns definition, add the following two lines:
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
