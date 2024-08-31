from django.urls import path, include

from . import views


app_name = "backoffice"

urlpatterns = [
    path('', views.index, name="index"),
    path('posts/', include("myblog.backoffice.posts.urls"))
]
