from django.urls import path

from . import views


app_name = "posts"

urlpatterns = [
    path('', views.index, name="index"),
    path('add/', views.add, name="add"),
    path('draft/<int:id>/', views.draft, name='draft'),
    path('publish/<int:id>/', views.publish, name='publish')
]
