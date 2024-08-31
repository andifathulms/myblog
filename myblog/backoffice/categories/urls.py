from django.urls import path

from . import views


app_name = "categories"

urlpatterns = [
    path('', views.index, name="index"),
    path('manage/', views.manage, name="manage"),
    path('manage/<int:id>/', views.manage, name='manage'),
    path('delete/<int:id>/', views.delete, name='delete')
]
