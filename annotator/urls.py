from django.urls import path, re_path
from django.views.generic.base import RedirectView

from . import views

app_name = 'annotator'
urlpatterns = [
	path('', views.home, name='home'),
    path('db_upload', views.db_upload, name='db_upload'),
    path('annotation_upload', views.annotation_upload, name='annotation_upload'),
    path('<int:entry_pk>/', views.index, name='index'),
    path('<int:entry_pk>/submit_belief', views.submit_belief, name='submit_belief'),
    path('<int:entry_pk>/change_view', views.change_view, name='change_view')
]