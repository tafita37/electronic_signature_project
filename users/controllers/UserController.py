# views.py
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST
from django.core.files.storage import FileSystemStorage
import os
import json
from web import settings 

@require_GET
def register_user_page(request):
    context = {
        "test": "Hello"
    }
    return render(request, "views/register_user.html", context)

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