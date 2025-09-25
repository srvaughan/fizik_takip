import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
import hashlib

DOSYA = "ogrenci_takip.xlsx"
KULLANICILAR_DOSYA = "kullanicilar.json"

# Örnek kullanıcılar (ilk kurulumda)
if not os.path.exists(KULLANICILAR_DOSYA):
    import json
    users = {
        "ogretmen": {"sifre": hashlib.sha256("ogretmen123".encode()).hexdigest(), "tip": "ogretmen"},
        "eren": {"sifre": hashlib.sha256("1234".encode()).hexdigest(), "tip": "ogrenci"}
    }
    with open(KULLANICILAR_DOSYA, "w") as f:
        json.dump(users, f)

# Login ekranı
st.title("Fizik Ders Takip Sistemi - Giriş")
with open(KULLANICILAR_DOSYA, "r") as f:
    users = json.load(f)

username = st.text_input("Kullanıcı Adı")
password = st.text_input("Şifre", type="password")

login_buton = st.button("Giriş Yap")

if login_buton:
    if username in users and users[username]['sifre'] == hashlib.sha256(password.encode()).hexdigest():
        st.success(f"Hoşgeldiniz {username}!")
        st.session_state['kullanici'] = username
        st.session_state['tip'] = users[username]['tip']
    else:
        st.error("Kullanıcı adı veya şifre hatalı!")

# Eğer giriş yapılmışsa ana uygulama
if 'kullanici' in st.session_state:
    st.sidebar.write(f"Giriş yapan: {st.session_state['kullanici']}")
    tip = st.session_state['tip']

    # Öğrenci listesi ve kaynak listesi
    if 'ogrenciler' not in st.session_state:
        st.session_state.ogrenciler = ["Eren"]
    if 'kaynaklar' not in st.session_state:
        if os.path.exists(DOSYA):
            df_all = pd.read_excel(DOSYA)
            st.session_state.kaynaklar = df_all['Kaynak'].dropna().unique().tolist() if not df_all.empty else []
        else:
            st.session_state.kaynaklar = []

    # Menüyü kullanıcı tipine göre ayarla
    if tip == 'ogretmen':
        menu = st.sidebar.selectbox("Menü", ["Tüm Öğrenciler Raporu", "Kayıt Ekle", "Deneme Sınavı Kaydı", "Haftalık Rapor", "Aylık Rapor", "Konu Bazlı Detay", "Tekrar Önerisi", "Başarı Takibi", "Grafik ve PDF Raporları"])
    else:
        menu = st.sidebar.selectbox("Menü", ["Kayıt Ekle", "Deneme Sınavı Kaydı", "Haftalık Rapor", "Aylık Rapor", "Konu Bazlı Detay", "Tekrar Önerisi", "Başarı Takibi", "Grafik ve PDF Raporları"])

    st.write(f"Seçilen Menü: {menu}")

    # Buradan itibaren mevcut tüm fonksiyon ve uygulama kodları (kayıt ekleme, rapor, tekrar önerisi vs.)
    # Öğrenci menüleri kendi verilerini görür, öğretmen menüleri tüm öğrencileri kapsar.