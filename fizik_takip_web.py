import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt

DOSYA = "ogrenci_takip.xlsx"
TYT_KONULAR = [
    "Fizik Bilimine Giriş",
    "Madde ve Özellikleri",
    "Sıvıların Kaldırma Kuvveti",
    "Katı Basıncı",
    "Durgun sıvı basıncı",
    "Gaz basıncı",
    "Akışkan basıncı",
    "Isı, Sıcaklık ve Genleşme",
    "Hareket ve Kuvvet",
    "İş, Güç ve Enerji",
    "Elektrostatik",
    "Elektrik Devreleri",
    "Manyetizma",
    "Dalgalar",
    "Optik"
]
AYT_KONULAR = [
    "Vektörler",
    "Tork ve Denge",
    "Kütle Merkezi",
    "Basit Makineler",
    "İvmeli Hareket",
    "Newton’un Hareket Yasaları",
    "İş, Güç ve Enerji II",
    "Atışlar",
    "İtme ve Momentum",
    "Elektrik Kuvvet",
    "Elektrik Alan", 
    "Elektriksel Potansiyel", 
    "Elektriksel Potansiyel Enerji",
    "Paralel Levhalar",
    "Sığa",
    "Manyetik Alan ve Manyetik Kuvvet",
    "İndüksiyon Emk'sı",
    "Alternatif Akım",
    "Transformatörler",
    "Çembersel Hareket",
    "Açısal Momentum",
    "Kütle Çekim ve Kepler Yasaları",
    "Basit Harmonik Hareket",
    "Dalga Mekaniği",
    "Elektromanyetik Dalgalar",
    "Atom Modelleri",
    "Büyük Patlama ve Parçacık Fiziği",
    "Radyoaktivite",
    "Özel Görelilik",
    "Kara Cisim Işıması",
    "Fotoelektrik Olay", 
    "Compton Olayı",
    "Modern Fiziğin Teknolojideki Uygulamaları"
]

if not os.path.exists(DOSYA):
    df = pd.DataFrame(columns=["Tarih", "Öğrenci", "Çalışma Türü", "Konu", "Kaynak", "Toplam Soru", "Doğru", "Yanlış", "Boş"])
    df.to_excel(DOSYA, index=False)

def veri_yukle():
    return pd.read_excel(DOSYA)

def kayit_ekle(tarih, ogrenci, calisma_turu, konu, kaynak, toplam, dogru, yanlis, bos):
    df = veri_yukle()
    yeni = pd.DataFrame([[tarih, ogrenci, calisma_turu, konu, kaynak, toplam, dogru, yanlis, bos]],
                        columns=["Tarih", "Öğrenci", "Çalışma Türü", "Konu", "Kaynak", "Toplam Soru", "Doğru", "Yanlış", "Boş"])
    df = pd.concat([df, yeni], ignore_index=True)
    df.to_excel(DOSYA, index=False)

# Öğrenci ve kaynak listesi
st.sidebar.subheader("Öğrenci Ekle")
if 'ogrenciler' not in st.session_state:
    st.session_state.ogrenciler = ["Eren"]
if 'kaynaklar' not in st.session_state:
    df_all = veri_yukle()
    st.session_state.kaynaklar = df_all['Kaynak'].dropna().unique().tolist() if not df_all.empty else []

yeni_ogrenci = st.sidebar.text_input("Yeni Öğrenci Adı")
if st.sidebar.button("Öğrenci Ekle"):
    if yeni_ogrenci and yeni_ogrenci not in st.session_state.ogrenciler:
        st.session_state.ogrenciler.append(yeni_ogrenci)
        st.success(f"{yeni_ogrenci} eklendi!")

st.title("Fizik Ders Takip Sistemi")
menu = st.sidebar.selectbox("Menü", ["Kayıt Ekle", "Haftalık Rapor", "Aylık Rapor", "Tekrar Önerisi", "Başarı Takibi", "Konu Bazlı Detay"])

if menu == "Kayıt Ekle":
    st.subheader("Yeni Kayıt Ekle")
    ogrenci = st.selectbox("Öğrenci", st.session_state.ogrenciler)
    calisma_turu = st.radio("Çalışma Türü", ["TYT", "AYT"])

    if calisma_turu == "TYT":
        konu = st.selectbox("Konu", TYT_KONULAR)
    else:
        konu = st.selectbox("Konu", AYT_KONULAR)

    secilen_kaynak = st.selectbox("Kaynak Seç", ["Yeni Kaynak"] + st.session_state.kaynaklar)
    if secilen_kaynak == "Yeni Kaynak":
        kaynak = st.text_input("Yeni Kaynak Adı")
    else:
        kaynak = secilen_kaynak

    tarih = st.date_input("Tarih")
    toplam = st.number_input("Toplam Soru", min_value=0)
    dogru = st.number_input("Doğru", min_value=0)
    yanlis = st.number_input("Yanlış", min_value=0)
    bos = st.number_input("Boş", min_value=0)

    if st.button("Kaydı Ekle"):
        if toplam != dogru+yanlis+bos:
            st.error("Toplam = Doğru + Yanlış + Boş olmalı!")
        elif not kaynak:
            st.error("Lütfen kaynak bilgisini girin!")
        else:
            kayit_ekle(tarih.strftime("%Y-%m-%d"), ogrenci, calisma_turu, konu, kaynak, toplam, dogru, yanlis, bos)
            if kaynak not in st.session_state.kaynaklar:
                st.session_state.kaynaklar.append(kaynak)
            st.success("Kayıt başarıyla eklendi!")

elif menu == "Tekrar Önerisi":
    calisma_turu_sec = st.radio("Çalışma Türü", ["TYT", "AYT", "Hepsi"], index=2)
    konular = TYT_KONULAR if calisma_turu_sec=='TYT' else AYT_KONULAR if calisma_turu_sec=='AYT' else TYT_KONULAR+AYT_KONULAR
    df = veri_yukle()
    df['Tarih'] = pd.to_datetime(df['Tarih'])
    liste = []
    for ogr in df['Öğrenci'].unique():
        for konu in konular:
            df_ok = df[(df['Öğrenci']==ogr)&(df['Konu']==konu)]
            if not df_ok.empty:
                son = df_ok['Tarih'].max()
                if (datetime.today()-son).days > 21:  # 3 hafta
                    liste.append((ogr, konu, son.strftime('%Y-%m-%d')))
    if liste:
        st.dataframe(pd.DataFrame(liste, columns=['Öğrenci','Konu','Son Çözüm Tarihi']))
    else:
        st.info("Tekrar önerilecek konu yok.")
