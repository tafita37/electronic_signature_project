# 📘 electronic_signature_tp

## 1. Overview

### 📝 Project description  
A Django-based practical project for implementing a simplified electronic signature system using RSA and SHA-256. It simulates both the user and a trusted certification authority (CA). The app allows for key generation, file signing, signature verification, and MITM attack simulation, offering hands-on learning about public key infrastructure (PKI) concepts.

### 🎯 Objective  
To provide a hands-on environment to understand digital signatures, RSA key management, SHA-256 hashing, and the risks associated with public key trust, all within a Django application.

---

## 2. Features

### ✅ Features list

- Public key registration with a simulated CA
- SHA-256 hashing of document contents
- Digital file signing using private key (PSS or PKCS1v15)
- Signature verification using registered public keys
- Timestamped signature metadata
- Man-in-the-middle (MITM) attack simulation (key substitution)
- Simplified certificate structure signed by the CA
- JSON-based key registry and signature storage
- File upload interface via Django

---

## 3. Requirements

### 🛠️ Required environment

- **Operating System**: Windows / Linux / macOS
- **Languages & Frameworks**: Python 3.10+, Django 4.x
- **Libraries**: `asgiref`, `Django`, `sqlparse`, `tzdata`

---

## 4. Installation

### Clone the repository

```bash
git https://github.com/tafita37/electronic_signature_project.git
cd electronic_signature_project
```

### Setup the project in the Odoo modules directory, create a virtual environment, install dependencies, and run the project:

```bash
pip install -r requirements.txt
python manage.py runserver
```