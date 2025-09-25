import json
import hashlib
import os

USERS_JSON = "kullanicilar.json"

def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()

# Eğer dosya yoksa oluştur
if os.path.exists(USERS_JSON):
    with open(USERS_JSON, "r") as f:
        users = json.load(f)
else:
    users = {}

# Admin şifresini tc6j7y olarak ayarla
users["admin"] = {"sifre": sha("tc6j7y"), "tip": "ogretmen"}

with open(USERS_JSON, "w") as f:
    json.dump(users, f, indent=4)

print("Admin şifresi başarıyla oluşturuldu/güncellendi. Artık 'tc6j7y' ile giriş yapabilirsiniz.")
