# views.py
import base64
from datetime import datetime
import hashlib
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST
from django.core.files.storage import FileSystemStorage
import os
import json
from web import settings 
from django.utils.text import get_valid_filename
from django.core.files.storage import default_storage
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature

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
    
@require_GET
def load_list_file_page(request):
    if 'user_name' not in request.session:
        return redirect('login_user_page')
    
    user_name = request.session['user_name']
    uploads_path = os.path.join(settings.BASE_DIR, "signature_file.json")
    try:
        with open(uploads_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    
    user_files = data.get(user_name, [])
    return render(request, "views/list_signature_file.html", {"user_files": user_files, "user_name": user_name, 'MEDIA_URL': settings.MEDIA_URL})

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
    return redirect('list_file_page')   

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
    return redirect('register_user_page')

@require_POST
def upload_file_to_sign(request):
    file_to_sign = request.FILES.get('file_to_sign')
    user_name = request.session.get('user_name')

    if not user_name or not file_to_sign:
        raise Exception("Utilisateur ou fichier non fourni.")

    # Refuse les fichiers non .txt
    if not file_to_sign.name.lower().endswith('.txt'):
        raise Exception("Le fichier à signer doit être au format .txt.")

    # Dossier utilisateur
    base_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', user_name)
    os.makedirs(base_dir, exist_ok=True)

    # Nom de fichier sécurisé
    original_name = get_valid_filename(file_to_sign.name)
    file_path = os.path.join(base_dir, original_name)

    # Gérer les doublons
    counter = 1
    file_root, file_ext = os.path.splitext(original_name)
    while os.path.exists(file_path):
        new_name = f"{file_root} ({counter}){file_ext}"
        file_path = os.path.join(base_dir, new_name)
        counter += 1

    final_filename = os.path.basename(file_path)

    # Sauvegarde du fichier
    with default_storage.open(file_path, 'wb+') as destination:
        for chunk in file_to_sign.chunks():
            destination.write(chunk)

    # Enregistrement JSON
    json_path = os.path.join(settings.BASE_DIR, "signature_file.json")
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            signature_files = json.load(f)
    else:
        signature_files = {}

    file_entry = {
        "unsigned_file": final_filename,
        "signed_file": ""
    }

    if user_name not in signature_files:
        signature_files[user_name] = [file_entry]
    else:
        signature_files[user_name].append(file_entry)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(signature_files, f, ensure_ascii=False, indent=4)

    return redirect('list_file_page')

def sha256_hash(message: str) -> str:
    # Convertir le message en bytes (UTF-8)
    message_bytes = message.encode('utf-8')
    
    # Calcul du hash
    sha256 = hashlib.sha256()
    sha256.update(message_bytes)
    
    # Retourne le hash au format hexadécimal
    return sha256.hexdigest()

@require_GET
def sign_file(request):
    file_name = request.GET.get('file_name')
    user_name = request.session.get('user_name')
    
    file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', user_name, file_name)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(content.encode('utf-8'))  
    hash_bytes = digest.finalize()
    
    private_key_path = os.path.join(settings.MEDIA_ROOT, f"{user_name}_private.pem")
    with open(private_key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    
    signature = private_key.sign(
        hash_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    signature_b64 = base64.b64encode(signature).decode('utf-8')
    
    sig_file_name = file_name.replace('.txt', '.sig')
    sig_file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', user_name, sig_file_name)
    with open(sig_file_path, 'wb') as sig_file:
        sig_file.write(signature)
        
    json_path = os.path.join(settings.BASE_DIR, "signature_file.json")
    with open(json_path, 'r', encoding='utf-8') as f:
        signature_files = json.load(f)
    signature_files[user_name]
    
    for i in range(0, len(signature_files[user_name])):
        if signature_files[user_name][i].get("unsigned_file") == file_name:
            signature_files[user_name][i]["signed_file"] = sig_file_name
            signature_files[user_name][i]["signature"] = signature_b64
            signature_files[user_name][i]["timestamp"] = timestamp = datetime.utcnow().isoformat() + "Z"
            break
        
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(signature_files, f, ensure_ascii=False, indent=4)
    return redirect('list_file_page')

@require_GET
def check_signature(request):
    file_name = request.GET.get('file_name')
    sig_file_name=file_name.replace('.txt', '.sig')
    user_name = request.session.get('user_name')
    
    file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', user_name, file_name)
    sig_file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', user_name, sig_file_name)
    with open(sig_file_path, 'rb') as sig_file:
        signature = sig_file.read()
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(content.encode('utf-8'))  
    hash_bytes = digest.finalize()
    
    public_key_path = os.path.join(settings.MEDIA_ROOT, f"{user_name}_public.pem")

    with open(public_key_path, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )
    print("vérification de la signature")
    try:
        public_key.verify(signature, hash_bytes, padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ), hashes.SHA256())
        print("Signature VALIDE")
    except InvalidSignature:
        print("Signature INVALIDE")
    return redirect('list_file_page')