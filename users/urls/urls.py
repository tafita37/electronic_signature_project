from django.urls import path
from users.controllers.UserController import check_signature, load_list_file_page, load_upload_file_page, login_user, login_user_page, register_user_page, register_user, sign_file, upload_file_to_sign

urlpatterns = [
    path('register_page/', register_user_page, name='register_user_page'),
    path('register_user/', register_user, name='register_user'),
    path('login_page/', login_user_page, name='login_user_page'),
    path('login_user/', login_user, name='login_user'),
    path('upload_file_page/', load_upload_file_page, name='upload_file_page'),
    path('list_file_page/', load_list_file_page, name='list_file_page'),
    path('upload_file_to_sign/', upload_file_to_sign, name='upload_file_to_sign'),
    path('sign_file/', sign_file, name='sign_file'),
    path('check_signature/', check_signature, name='check_signature'),
]