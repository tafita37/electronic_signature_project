from django.urls import path
from users.controllers.UserController import register_user_page, register_user

urlpatterns = [
    path('register_page/', register_user_page, name='register_user_page'),
    path('register_user/', register_user, name='register_user'),
]