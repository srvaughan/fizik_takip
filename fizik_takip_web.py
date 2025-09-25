# fizik_takip_web.py
import streamlit as st
import pandas as pd
import os
import json
import hashlib
from datetime import datetime, timedelta
from io import BytesIO
import matplotlib.pyplot as plt
from fpdf import FPDF

# ---------------- Config ----------------
DATA_XLSX = "ogrenci_takip.xlsx"
USERS_JSON = "kullanicilar.json"

TYT_KONULAR = [
    "Fizik Bilimine Giriş", "Madde ve Özellikleri", "Sıvıların Kaldırma Kuvveti",
    "Katı Basıncı", "Durgun sıvı basıncı", "Gaz basıncı", "Akışkan basıncı",
    "Isı, Sıcaklık ve Genleşme", "Hareket ve Kuvvet", "İş, Güç ve Enerji",
    "Elektrostatik", "Elektrik Devreleri", "Manyetizma", "Dalgalar", "Optik"
]

AYT_KONULAR = [
    "Vektörler", "Tork ve Denge", "Kütle Merkezi", "Basit Makineler",
    "İvmeli Hareket", "Newton’un Hareket Yasaları", "İş, Güç ve Enerji II",
    "Atışlar", "İtme ve Momentum", "Elektrik Kuvvet", "Elektrik Alan",
    "Elektriksel Potansiyel", "Elektriksel Potansiyel Enerji", "Paralel Levhalar",
    "Sığa", "Manyetik Alan ve Manyetik Kuvvet", "İndüksiyon Emk'sı",
    "Alternatif Akım", "Transformatörler", "Çembersel Hareket", "Açısal Momentum",
    "Kütle Çekim ve Kepler Yasaları", "Basit Harmonik Hareket", "Dalga Mekaniği",
    "Elektromanyetik Dalgalar", "Atom Modelleri", "Büyük Patlama ve Parçacık Fiziği",
    "Radyoaktivite", "Özel Görelilik", "Kara Cisim Işıması", "Fotoelektrik Olay",
    "Compton Olayı", "Modern Fiziğin Teknolojideki Uygulamaları"
]

# ---------------- Helpers ----------------
def sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def ensure_files():
    # users file with admin
    if not os.path.exists(USERS_JSON):
        admin_pw = sha("tc6j7y")
        with open(USERS_JSON, "w") as f:
            json.dump({"admin": {"sifre": admin_pw, "tip": "ogretmen"}}, f)
    # data excel with two sheets
    if not os.path.exists(DATA_XLSX):
        # empty dataframes
        calisma = pd.DataFrame(columns=["Tarih","Öğrenci","Çalışma Türü","Konu","Kaynak","Toplam Soru","Doğru","Yanlış","Boş"])
        deneme = pd.DataFrame(columns=["Tarih","Öğrenci","Sınav Adı","Çalışma Türü","Konu","Toplam Soru","Doğru","Yanlış","Boş"])
        with pd.ExcelWriter(DATA_XLSX, engine="openpyxl") as w:
            calisma.to_excel(w, sheet_name="Calisma", index=False)
            deneme.to_excel(w, sheet_name="Deneme", index=False)

def load_data():
    ensure_files()
    xls = pd.read_excel(DATA_XLSX, sheet_name=None)
    calisma = xls.get("Calisma", pd.DataFrame(columns=["Tarih","Öğrenci","Çalışma Türü","Konu","Kaynak","Toplam Soru","Doğru","Yanlış","Boş"]))
    deneme = xls.get("Deneme", pd.DataFrame(columns=["Tarih","Öğrenci","Sınav Adı","Çalışma Türü","Konu","Toplam Soru","Doğru","Yanlış","Boş"]))
    return calisma, deneme

def save_data(calisma_df, deneme_df):
    with pd.ExcelWriter(DATA_XLSX, engine="openpyxl") as w:
        calisma_df.to_excel(w, sheet_name="Calisma", index=False)
        deneme_df.to_excel(w, sheet_name="Deneme", index=False)

def load_users():
    ensure_files()
    with open(USERS_JSON, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_JSON, "w") as f:
        json.dump(users, f)

# ---------------- App ----------------
st.set_page_config(page_title="Fizik Takip", layout="wide")
st.title("Fizik Ders Takip Sistemi")

# initialize session
if "user" not in st.session_state:
    st.session_state["user"] = None  # dict: {"ad":..., "tip":...}

# Login / Register UI
if st.session_state["user"] is None:
    users = load_users()
    col1, col2 = st.columns([1,1])
    with col1:
        st.subheader("Giriş Yap")
        user = st.text_input("Kullanıcı Adı", key="login_user")
        pwd = st.text_input("Şifre", type="password", key="login_pwd")
        if st.button("Giriş Yap"):
            users = load_users()
            if user in users and users[user]["sifre"] == sha(pwd):
                st.success(f"Hoşgeldiniz, {user}!")
                st.session_state["user"] = {"ad": user, "tip": users[user]["tip"]}
                st.experimental_rerun()
            else:
                st.error("Kullanıcı adı veya şifre hatalı.")
    with col2:
        st.subheader("Kayıt Ol (Öğrenci)")
        new_user = st.text_input("Kullanıcı Adı (yeni)", key="reg_user")
        new_pwd = st.text_input("Şifre (yeni)", type="password", key="reg_pwd")
        if st.button("Kayıt Ol"):
            users = load_users()
            if not new_user or not new_pwd:
                st.error("Kullanıcı adı ve şifre boş olamaz.")
            elif new_user in users:
                st.error("Bu kullanıcı adı zaten alınmış.")
            else:
                users[new_user] = {"sifre": sha(new_pwd), "tip": "ogrenci"}
                save_users(users)
                st.success("Kayıt başarılı. Giriş yapabilirsiniz.")
    st.stop()

# logged in
me = st.session_state["user"]["ad"]
role = st.session_state["user"]["tip"]
left, right = st.columns([1,5])
with left:
    st.write(f"**Kullanıcı:** {me} ({role})")
    if st.button("Çıkış"):
        st.session_state["user"] = None
        st.experimental_rerun()

# load data
calisma_df, deneme_df = load_data()

# helper: get student list
all_students = sorted(list(set(calisma_df["Öğrenci"].dropna().tolist() + deneme_df["Öğrenci"].dropna().tolist() + ([] if role=="ogretmen" else [me]))))

# Menu
if role == "ogretmen":
    menu = st.sidebar.selectbox("Menü", [
        "📊 Öğretmen Raporları",
        "Kayıt Ekle",
        "Deneme Sınavı Ekle",
        "Haftalık Rapor",
        "Aylık Rapor",
        "Konu Bazlı Detay",
        "Tekrar Önerisi",
        "Başarı Takibi"
    ])
else:
    menu = st.sidebar.selectbox("Menü", [
        "Kayıt Ekle",
        "Deneme Sınavı Ekle",
        "Haftalık Rapor",
        "Aylık Rapor",
        "Konu Bazlı Detay",
        "Tekrar Önerisi",
        "Başarı Takibi"
    ])

# ---------- Öğretmen Raporları (admin-only) ----------
if menu == "📊 Öğretmen Raporları":
    st.header("Öğretmen Raporları (sadece öğretmen görür)")
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        filt_tarih1 = st.date_input("Başlangıç", datetime.today() - timedelta(days=30))
    with col2:
        filt_tarih2 = st.date_input("Bitiş", datetime.today())
    with col3:
        filt_calisma = st.selectbox("Çalışma Türü", ["Hepsi","TYT","AYT"])
    # aggregate combined
    cal = calisma_df.copy(); den = deneme_df.copy()
    cal["Tarih"] = pd.to_datetime(cal["Tarih"]); den["Tarih"] = pd.to_datetime(den["Tarih"])
    mask_cal = (cal["Tarih"]>=pd.to_datetime(filt_tarih1)) & (cal["Tarih"]<=pd.to_datetime(filt_tarih2))
    mask_den = (den["Tarih"]>=pd.to_datetime(filt_tarih1)) & (den["Tarih"]<=pd.to_datetime(filt_tarih2))
    cal_f = cal[mask_cal]
    den_f = den[mask_den]
    if filt_calisma != "Hepsi":
        cal_f = cal_f[cal_f["Çalışma Türü"]==filt_calisma]
        den_f = den_f[den_f["Çalışma Türü"]==filt_calisma]
    # summary per student
    if cal_f.empty and den_f.empty:
        st.info("Seçilen aralıkta veri yok.")
    else:
        # combine by summing totals for same student & topic
        cal_agg = cal_f.groupby(["Öğrenci","Konu"]).agg({"Toplam Soru":"sum","Doğru":"sum"}).reset_index()
        den_agg = den_f.groupby(["Öğrenci","Konu"]).agg({"Toplam Soru":"sum","Doğru":"sum"}).reset_index()
        combined = pd.concat([cal_agg, den_agg], ignore_index=True)
        combined = combined.groupby(["Öğrenci","Konu"]).sum().reset_index()
        combined["Başarı (%)"] = (combined["Doğru"] / combined["Toplam Soru"] * 100).round(1)
        st.subheader("Öğrenci - Konu Bazlı Özet")
        st.dataframe(combined)
        # download excel
        buf = BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            combined.to_excel(w, index=False, sheet_name="Özet")
        st.download_button("Excel İndir", data=buf.getvalue(), file_name="ogretmen_ozet.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ---------- Kayıt Ekle ----------
elif menu == "Kayıt Ekle":
    st.header("Günlük Çalışma Kaydı Ekle")
    # which student: teacher can add for any student, student only themselves
    if role == "ogretmen":
        ogr = st.selectbox("Öğrenci", all_students)
    else:
        ogr = me
    calisma_turu = st.radio("Çalışma Türü", ["TYT","AYT"])
    konular = TYT_KONULAR if calisma_turu=="TYT" else AYT_KONULAR
    konu = st.selectbox("Konu", konular)
    kaynak = st.text_input("Kaynak (kitap/deneme/test adı)")
    tarih = st.date_input("Tarih", datetime.today())
    toplam = st.number_input("Toplam Soru", min_value=0, value=0)
    dogru = st.number_input("Doğru", min_value=0, value=0)
    yanlis = st.number_input("Yanlış", min_value=0, value=0)
    bos = st.number_input("Boş", min_value=0, value=0)
    if st.button("Kaydı Ekle"):
        if toplam != dogru + yanlis + bos:
            st.error("Toplam = Doğru + Yanlış + Boş olmalı!")
        else:
            calisma_df = calisma_df.append({
                "Tarih": tarih.strftime("%Y-%m-%d"),
                "Öğrenci": ogr,
                "Çalışma Türü": calisma_turu,
                "Konu": konu,
                "Kaynak": kaynak,
                "Toplam Soru": toplam,
                "Doğru": dogru,
                "Yanlış": yanlis,
                "Boş": bos
            }, ignore_index=True)
            save_data(calisma_df, deneme_df)
            st.success("Çalışma kaydedildi.")

# ---------- Deneme Sınavı Ekle ----------
elif menu == "Deneme Sınavı Ekle":
    st.header("Deneme Sınavı - Konu Bazlı Kayıt")
    if role == "ogretmen":
        ogr = st.selectbox("Öğrenci", all_students)
    else:
        ogr = me
    sinav_adi = st.text_input("Deneme / Sınav Adı")
    tarih = st.date_input("Tarih", datetime.today())
    calisma_turu = st.radio("Çalışma Türü", ["TYT","AYT"])
    konular = TYT_KONULAR if calisma_turu=="TYT" else AYT_KONULAR
    secilen_konular = st.multiselect("Konular (birden fazla seçip ayrı ayrı gir)", konular)
    if secilen_konular:
        st.write("Seçilen konular için verileri girip 'Deneme Kaydet' butonuna basın.")
    for konu in secilen_konular:
        st.markdown(f"**{konu}**")
        t = st.number_input(f"{konu} - Toplam", min_value=0, key=f"den_top_{konu}")
        d = st.number_input(f"{konu} - Doğru", min_value=0, key=f"den_dog_{konu}")
        y = st.number_input(f"{konu} - Yanlış", min_value=0, key=f"den_yan_{konu}")
        b = st.number_input(f"{konu} - Boş", min_value=0, key=f"den_bos_{konu}")
        if st.button(f"{konu} - Deneme Kaydet"):
            if t != d + y + b:
                st.error("Toplam = Doğru + Yanlış + Boş olmalı!")
            else:
                deneme_df = deneme_df.append({
                    "Tarih": tarih.strftime("%Y-%m-%d"),
                    "Öğrenci": ogr,
                    "Sınav Adı": sinav_adi,
                    "Çalışma Türü": calisma_turu,
                    "Konu": konu,
                    "Toplam Soru": t,
                    "Doğru": d,
                    "Yanlış": y,
                    "Boş": b
                }, ignore_index=True)
                save_data(calisma_df, deneme_df)
                st.success(f"{konu} için deneme kaydedildi.")

# ---------- Haftalık Rapor ----------
elif menu == "Haftalık Rapor":
    st.header("Haftalık Rapor (son 7 gün)")
    dfc, dfd = load_data()
    dfc["Tarih"] = pd.to_datetime(dfc["Tarih"])
    son = datetime.today() - timedelta(days=7)
    df_son = dfc[dfc["Tarih"] >= son]
    if role != "ogretmen":
        df_son = df_son[df_son["Öğrenci"]==me]
    if df_son.empty:
        st.info("Son 7 gün içinde kayıt yok.")
    else:
        rpt = df_son.groupby(["Öğrenci","Çalışma Türü","Konu"]).agg({"Toplam Soru":"sum","Doğru":"sum","Yanlış":"sum","Boş":"sum"}).reset_index()
        rpt["Doğru Oranı (%)"] = (rpt["Doğru"]/rpt["Toplam Soru"]*100).round(1)
        st.dataframe(rpt)

# ---------- Aylık Rapor ----------
elif menu == "Aylık Rapor":
    st.header("Tarih Aralığına Göre Rapor")
    start = st.date_input("Başlangıç", datetime.today() - timedelta(days=30))
    end = st.date_input("Bitiş", datetime.today())
    dfc, dfd = load_data()
    dfc["Tarih"] = pd.to_datetime(dfc["Tarih"])
    mask = (dfc["Tarih"]>=pd.to_datetime(start)) & (dfc["Tarih"]<=pd.to_datetime(end))
    df_period = dfc[mask]
    if role != "ogretmen":
        df_period = df_period[df_period["Öğrenci"]==me]
    if df_period.empty:
        st.info("Seçilen aralıkta çalışma yok.")
    else:
        rpt = df_period.groupby(["Öğrenci","Çalışma Türü","Konu"]).agg({"Toplam Soru":"sum","Doğru":"sum","Yanlış":"sum","Boş":"sum"}).reset_index()
        rpt["Doğru Oranı (%)"] = (rpt["Doğru"]/rpt["Toplam Soru"]*100).round(1)
        st.dataframe(rpt)

# ---------- Konu Bazlı Detay ----------
elif menu == "Konu Bazlı Detay":
    st.header("Konu Bazlı Detay")
    calisma_turu = st.radio("Çalışma Türü", ["TYT","AYT"])
    konular = TYT_KONULAR if calisma_turu=="TYT" else AYT_KONULAR
    konu = st.selectbox("Konu", konular)
    # combine both calisma and deneme for this konu
    dfc, dfd = load_data()
    dfc["Tarih"] = pd.to_datetime(dfc["Tarih"]); dfd["Tarih"] = pd.to_datetime(dfd["Tarih"])
    df_k = pd.concat([
        dfc[(dfc["Konu"]==konu) & (dfc["Çalışma Türü"]==calisma_turu)],
        dfd[(dfd["Konu"]==konu) & (dfd["Çalışma Türü"]==calisma_turu)]
    ], ignore_index=True)
    if role != "ogretmen":
        df_k = df_k[df_k["Öğrenci"]==me]
    if df_k.empty:
        st.info("Bu konuda kayıt yok.")
    else:
        df_k["Başarı (%)"] = (df_k["Doğru"]/df_k["Toplam Soru"]*100).round(1)
        st.dataframe(df_k.sort_values("Tarih"))

        # plot trend per student
        for ogr in df_k["Öğrenci"].unique():
            df_ogr = df_k[df_k["Öğrenci"]==ogr].sort_values("Tarih")
            fig, ax = plt.subplots()
            ax.plot(df_ogr["Tarih"], df_ogr["Başarı (%)"], marker="o")
            ax.set_title(f"{ogr} - {konu}")
            ax.set_ylim(0,100)
            st.pyplot(fig)

# ---------- Tekrar Önerisi (Hafta / Deneme / Mix) ----------
elif menu == "Tekrar Önerisi":
    st.header("Tekrar Önerisi")
    tab1, tab2, tab3 = st.tabs(["Çalışma Bazlı (hafta filtresi)", "Deneme Bazlı", "Mix (Çalışma+Deneme)"])

    # common mapping
    hafta_map = {"3 hafta":21,"4 hafta":28,"5 hafta":35,"6+ hafta":42}

    with tab1:
        st.subheader("Çalışma Bazlı")
        hafta_sec = st.selectbox("Hafta filtre", list(hafta_map.keys()), index=0, key="t1_h")
        calisma_turu = st.radio("Çalışma Türü", ["Hepsi","TYT","AYT"], key="t1_ct")
        basari_alt = st.slider("Başarı alt limiti (%)", 0,100,60, key="t1_b")
        cal, den = load_data()
        cal["Tarih"] = pd.to_datetime(cal["Tarih"])
        ogr_list = [me] if role!="ogretmen" else sorted(cal["Öğrenci"].unique())
        rows=[]
        for ogr in ogr_list:
            for konu in (TYT_KONULAR+AYT_KONULAR):
                df_ok = cal[(cal["Öğrenci"]==ogr) & (cal["Konu"]==konu)]
                if df_ok.empty:
                    continue
                if calisma_turu!="Hepsi" and not (df_ok["Çalışma Türü"]==calisma_turu).any():
                    continue
                son = df_ok["Tarih"].max()
                gun = (datetime.today()-son).days
                basari = (df_ok["Doğru"].sum()/df_ok["Toplam Soru"].sum()*100).round(1)
                if gun >= hafta_map[hafta_sec] or basari <= basari_alt:
                    rows.append((ogr,konu,son.strftime("%Y-%m-%d"),gun,basari))
        if rows:
            df_out = pd.DataFrame(rows, columns=["Öğrenci","Konu","Son Çözüm","Gün Önce","Başarı (%)"])
            st.dataframe(df_out)
        else:
            st.info("Tekrar önerilecek konu yok.")

    with tab2:
        st.subheader("Deneme Bazlı (yanlış+boş ağırlıklı)")
        calisma_turu = st.radio("Çalışma Türü", ["Hepsi","TYT","AYT"], key="t2_ct")
        basari_alt = st.slider("Başarı alt limiti (%)", 0,100,60, key="t2_b")
        den = load_data()[1]
        den["Tarih"] = pd.to_datetime(den["Tarih"])
        ogr_list = [me] if role!="ogretmen" else sorted(den["Öğrenci"].unique())
        rows=[]
        for ogr in ogr_list:
            for konu in (TYT_KONULAR+AYT_KONULAR):
                df_ok = den[(den["Öğrenci"]==ogr) & (den["Konu"]==konu)]
                if df_ok.empty:
                    continue
                if calisma_turu!="Hepsi" and not (df_ok["Çalışma Türü"]==calisma_turu).any():
                    continue
                total = df_ok["Toplam Soru"].sum()
                correct = df_ok["Doğru"].sum()
                basari = (correct/total*100).round(1) if total>0 else 0.0
                if basari <= basari_alt:
                    last = df_ok["Tarih"].max()
                    rows.append((ogr,konu,last.strftime("%Y-%m-%d"),basari))
        if rows:
            df_out = pd.DataFrame(rows, columns=["Öğrenci","Konu","Son Deneme Tarihi","Başarı (%)"])
            st.dataframe(df_out)
        else:
            st.info("Denemelere göre tekrar gerektiren konu yok.")

    with tab3:
        st.subheader("Mix (Çalışma + Deneme)")
        hafta_sec = st.selectbox("Hafta filtre", list(hafta_map.keys()), index=0, key="t3_h")
        calisma_turu = st.radio("Çalışma Türü", ["Hepsi","TYT","AYT"], key="t3_ct")
        basari_alt = st.slider("Başarı alt limiti (%)", 0,100,60, key="t3_b")

        cal, den = load_data()
        cal["Tarih"] = pd.to_datetime(cal["Tarih"]); den["Tarih"] = pd.to_datetime(den["Tarih"])
        ogr_list = [me] if role!="ogretmen" else sorted(set(cal["Öğrenci"].unique()).union(set(den["Öğrenci"].unique())))
        rows=[]
        for ogr in ogr_list:
            for konu in (TYT_KONULAR+AYT_KONULAR):
                # çalışma bazlı
                df_c = cal[(cal["Öğrenci"]==ogr)&(cal["Konu"]==konu)]
                df_d = den[(den["Öğrenci"]==ogr)&(den["Konu"]==konu)]
                last_dates = []
                correct_total = 0
                total_q = 0
                if not df_c.empty:
                    last_dates.append(df_c["Tarih"].max())
                    total_q += df_c["Toplam Soru"].sum()
                    correct_total += df_c["Doğru"].sum()
                if not df_d.empty:
                    last_dates.append(df_d["Tarih"].max())
                    total_q += df_d["Toplam Soru"].sum()
                    correct_total += df_d["Doğru"].sum()
                if total_q==0:
                    continue
                last = max(last_dates)
                gun = (datetime.today()-last).days
                basari = (correct_total/total_q*100).round(1)
                if gun >= hafta_map[hafta_sec] or basari <= basari_alt:
                    rows.append((ogr,konu,last.strftime("%Y-%m-%d"),gun,basari))
        if rows:
            df_out = pd.DataFrame(rows, columns=["Öğrenci","Konu","Son Çözüm","Gün Önce","Başarı (%)"])
            st.dataframe(df_out)
        else:
            st.info("Mix kriterlerine göre tekrar önerisi yok.")

# ---------- Başarı Takibi ----------
elif menu == "Başarı Takibi":
    st.header("Başarı Takibi (konu bazlı)")
    cal, den = load_data()
    comb = pd.concat([cal[["Öğrenci","Çalışma Türü","Konu","Toplam Soru","Doğru"]],
                      den[["Öğrenci","Çalışma Türü","Konu","Toplam Soru","Doğru"]]], ignore_index=True)
    if role!="ogretmen":
        comb = comb[comb["Öğrenci"]==me]
    if comb.empty:
        st.info("Henüz veri yok.")
    else:
        rpt = comb.groupby(["Öğrenci","Çalışma Türü","Konu"]).sum().reset_index()
        rpt["Başarı (%)"] = (rpt["Doğru"]/rpt["Toplam Soru"]*100).round(1)
        st.dataframe(rpt)

# ---------------- end menu ----------------

# Save (in case other parts modified df references)
save_data(calisma_df, deneme_df)
