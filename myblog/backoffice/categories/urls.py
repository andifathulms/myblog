from django.urls import path

from . import views


app_name = "categories"

urlpatterns = [
    path('', views.index, name="index"),
    path('manage/', views.manage, name="manage"),
    path('<int:id>/', views.manage, name='manage')
]
