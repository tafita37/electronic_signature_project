from django.urls import path
from users.controllers.UserController import load_upload_file_page, login_user, login_user_page, register_user_page, register_user, upload_file_to_sign

urlpatterns = [
    path('register_page/', register_user_page, name='register_user_page'),
    path('register_user/', register_user, name='register_user'),
    path('login_page/', login_user_page, name='login_user_page'),
    path('login_user/', login_user, name='login_user'),
    path('upload_file_page/', load_upload_file_page, name='upload_file_page'),
    path('upload_file_to_sign/', upload_file_to_sign, name='upload_file_to_sign'),
]