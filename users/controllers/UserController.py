# views.py
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST
from django.core.files.storage import FileSystemStorage
import os
import json
from web import settings 
from django.utils.text import get_valid_filename
from django.core.files.storage import default_storage

@require_GET
def register_user_page(request):
    context = {
        "css_css" : ['vertical-layout-light/style.css'],
    }
    return render(request, "views/register_user.html", context)

@require_GET
def login_user_page(request):
    return render(request, "views/login_user.html")

@require_GET
def load_upload_file_page(request):
    if 'user_name' not in request.session:
        return redirect('login_user_page')
    else :
        return render(request, "views/upload_signature_file.html")

@require_POST
def login_user(request):
    user_name = request.POST.get('user_name')
    registre_path = os.path.join(settings.BASE_DIR, "registre.json")
    if os.path.exists(registre_path):
        with open(registre_path, "r", encoding="utf-8") as f:
            registre = json.load(f)
            if user_name not in registre :
                raise Exception("L'utilisateur n'existe pas.")
    request.session['user_name'] = user_name
    return redirect('upload_file_page')   

@require_POST
def register_user(request):
    user_name = request.POST.get('user_name')
    public_key = request.FILES.get('public_key')
    if not user_name :
        raise Exception("Le nom d'utilisateur ne peut pas être vide.")
    if public_key:
        extension = os.path.splitext(public_key.name)[1]
        if extension.lower() != '.pem':
            raise Exception("Le fichier de clé publique doit être au format PEM (.pem).")
        new_filename = f"{user_name}_public{extension}"
        fs = FileSystemStorage()
        filename = fs.save(new_filename, public_key)
        uploaded_file_url = fs.url(filename)
        print(f"Fichier renommé et sauvegardé à : {uploaded_file_url}")
        registre_path = os.path.join(settings.BASE_DIR, "registre.json")
        if os.path.exists(registre_path):
            with open(registre_path, "r", encoding="utf-8") as f:
                registre = json.load(f)
        else:
            registre = {}
        registre[user_name] = new_filename
        with open(registre_path, "w", encoding="utf-8") as f:
            json.dump(registre, f, ensure_ascii=False, indent=4)
    print(user_name, public_key)
    return redirect('register_user_page')

@require_POST
def upload_file_to_sign(request):
    file_to_sign = request.FILES.get('file_to_sign')
    user_name = request.session.get('user_name')

    # Refuse si ce n’est pas un fichier .txt
    if not file_to_sign.name.lower().endswith('.txt'):
        raise Exception("Le fichier de clé publique doit être au format texte (.txt).")

    base_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', user_name)
    os.makedirs(base_dir, exist_ok=True)

    original_name = get_valid_filename(file_to_sign.name)
    file_path = os.path.join(base_dir, original_name)

    # Gestion des doublons : ajout de (1), (2), ...
    counter = 1
    file_root, file_ext = os.path.splitext(original_name)
    while os.path.exists(file_path):
        new_name = f"{file_root} ({counter}){file_ext}"
        file_path = os.path.join(base_dir, new_name)
        counter += 1
    
    with default_storage.open(file_path, 'wb+') as destination:
        for chunk in file_to_sign.chunks():
            destination.write(chunk)

    return redirect('upload_file_page')