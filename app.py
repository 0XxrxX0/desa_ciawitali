import streamlit as st
import pandas as pd
import plotly.express as px
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Dashboard Kepuasan Masyarakat",
    page_icon="📊",
    layout="wide"
)

# ==========================================
# ⚙️ PENGATURAN SUMBER DATA & SKALA
# ==========================================
# Cek apakah ada secrets (untuk deploy), jika tidak ada pakai dummy/kosong
try:
    GOOGLE_SHEET_URL = st.secrets["google_sheet_url"]
except FileNotFoundError:
    # Ini optional, buat jaga-jaga kalau dijalankan lokal tanpa setup secrets
    GOOGLE_SHEET_URL = ""
LOCAL_FILE_NAME = "Survey Kepuasan Masyarakat.csv"
TARGET_SCORE = 4.0  # Target nilai yang dianggap "Baik" untuk skala 1-5
MAX_SCALE = 5.0     # Skala maksimal kuesioner
# ==========================================

# --- FUNGSI MEMBERSIHKAN PEKERJAAN ---
def clean_job_titles(df, column_name, top_n=6):
    if column_name not in df.columns:
        return df
    # Standarisasi teks
    df[column_name] = df[column_name].astype(str).str.strip().str.title()
    # Kelompokkan yang sedikit menjadi 'Lainnya'
    top_jobs = df[column_name].value_counts().nlargest(top_n).index.tolist()
    df[column_name] = df[column_name].apply(lambda x: x if x in top_jobs else 'Pekerjaan Lainnya')
    return df

# --- FUNGSI LOAD DATA (AUTO-FALLBACK) ---
@st.cache_data(ttl=60)
def load_data():
    source_status = ""
    error_msg = ""
    df = pd.DataFrame()

    # COBA 1: Load dari Google Sheet (Online)
    try:
        df = pd.read_csv(GOOGLE_SHEET_URL)
        source_status = "online"
    except Exception as e:
        # COBA 2: Load dari File Lokal (Offline)
        error_msg = str(e)
        try:
            df = pd.read_csv(LOCAL_FILE_NAME)
            source_status = "offline"
        except Exception as e_local:
            return None, "critical", f"Gagal memuat data. Error: {e_local}"

    # --- MAPPING KOLOM ---
    column_mapping = {
        'Cap waktu': 'Timestamp',
        '1. Nama Lengkap': 'Nama',
        '2. Umur': 'Umur',
        '3. Jenis Kelamin': 'Jenis Kelamin',
        '4. Jenjang Pendidikan': 'Pendidikan',
        '5. Pekerjaan': 'Pekerjaan',
        '6. Bagaimana pendapat saudara tentang perilaku petugas dalam memberikan pelayanan?': 'Q1_Perilaku',
        '7. Bagaimana pendapat saudara tentang biaya/tarif pelayanan yg ditetapkan oleh petugas pelayanan?': 'Q2_Biaya',
        '8. Bagaimana pendapat saudara tentang waktu yang diperlukan untuk mendapatkan produk layanan?': 'Q3_Waktu',
        '9. Bagaimana pendapat saudara tentang prosedur yang harus ditempuh untuk mendapatkan pelayanan?': 'Q4_Prosedur',
        '10. Bagaimana pendapat saudara antara jenis pelayanan yang yg di mohon dengan persyaratan yg diminta oleh petugas pelayanan, apakah sesuai atau tidak?': 'Q5_Kesesuaian',
        '11. Bagaimana pendapat saudara untuk tentang kemampuan petugas dalam memberikan pelayanan ': 'Q6_Kemampuan',
        '12. Bagaimana pendapat saudara tentang penanganan pengaduan masyarakat oleh petugas pelayanan?': 'Q7_Pengaduan',
        '13. Bagaimana pendapat saudara tentang keberadaan maklumat / janji pelayanan?': 'Q8_Maklumat',
        '14. Berapa menurut anda nilai peringkat pelayanan yg dilakukan oleh petugas?': 'Q9_Rating_Total',
        '15. Apakah saudara memiliki sebuah laporan/keluhan saudara yang ingin di sampaikan ke kantor desa': 'Feedback',
        'Bukti untuk pelaporan/keluhan jika ada': 'Bukti'
    }
    
    # Rename kolom dengan aman
    try:
        df = df.rename(columns=column_mapping)
    except:
        pass
    
    # Konversi data numerik & waktu
    if 'Umur' in df.columns:
        df['Umur'] = pd.to_numeric(df['Umur'], errors='coerce')
    if 'Timestamp' in df.columns:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        df = df.sort_values('Timestamp', ascending=False)
        
    # Rapikan Pekerjaan
    if 'Pekerjaan' in df.columns:
        df = clean_job_titles(df, 'Pekerjaan', top_n=5)

    return df, source_status, error_msg

# --- LOAD DATA UTAMA ---
df_raw, status, msg = load_data()

if status == "critical":
    st.error("⛔ Terjadi Kesalahan Fatal! Data tidak ditemukan.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.header("🎛️ Panel Kontrol")
    if status == "online":
        st.success("🟢 Online (Live)")
    else:
        st.warning("🟠 Offline (Lokal)")
    
    if st.button("🔄 Segarkan Data"):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.subheader("Filter Data")
    
    # Filter Gender
    gender_opts = ["Semua"] + sorted(list(df_raw['Jenis Kelamin'].dropna().unique()))
    gender_filter = st.selectbox("Jenis Kelamin", gender_opts)
    
    # Filter Pendidikan
    edu_opts = ["Semua"] + sorted(list(df_raw['Pendidikan'].dropna().unique()))
    edu_filter = st.selectbox("Pendidikan", edu_opts)
    
    # Filter Pekerjaan
    job_opts = ["Semua"] + sorted(list(df_raw['Pekerjaan'].dropna().unique()))
    job_filter = st.selectbox("Pekerjaan", job_opts)

# --- FILTERING ---
df_filtered = df_raw.copy()
if gender_filter != "Semua":
    df_filtered = df_filtered[df_filtered['Jenis Kelamin'] == gender_filter]
if edu_filter != "Semua":
    df_filtered = df_filtered[df_filtered['Pendidikan'] == edu_filter]
if job_filter != "Semua":
    df_filtered = df_filtered[df_filtered['Pekerjaan'] == job_filter]

# --- HALAMAN UTAMA ---
st.title("📊 Dashboard Kepuasan Masyarakat")
st.markdown(f"**Total Responden:** {len(df_filtered)} Orang")
st.markdown("---")

# 1. METRIK UTAMA (UPDATED SKALA 1-5)
col1, col2, col3, col4 = st.columns(4)

# Definisi kolom skor
score_cols = ['Q1_Perilaku', 'Q2_Biaya', 'Q3_Waktu', 'Q4_Prosedur', 
              'Q5_Kesesuaian', 'Q6_Kemampuan', 'Q7_Pengaduan', 
              'Q8_Maklumat', 'Q9_Rating_Total']
existing_cols = [c for c in score_cols if c in df_filtered.columns]

# Hitung nilai
total_resp = len(df_filtered)
avg_age = df_filtered['Umur'].mean() if total_resp > 0 and 'Umur' in df_filtered.columns else 0
ikm_score = df_filtered[existing_cols].mean().mean() if existing_cols and total_resp > 0 else 0
rating_total = df_filtered['Q9_Rating_Total'].mean() if total_resp > 0 and 'Q9_Rating_Total' in df_filtered.columns else 0

with col1:
    st.metric("👥 Total Responden", f"{total_resp}")
with col2:
    st.metric("🎂 Rata-rata Umur", f"{avg_age:.1f} Th")
with col3:
    # UPDATED: Menggunakan MAX_SCALE (5.0) dan TARGET_SCORE (4.0)
    st.metric("⭐ Indeks Kepuasan", f"{ikm_score:.2f} / {MAX_SCALE}", delta=f"{ikm_score-TARGET_SCORE:.2f}")
with col4:
    # UPDATED: Menggunakan MAX_SCALE (5.0)
    st.metric("🏆 Rating Akhir", f"{rating_total:.2f} / {MAX_SCALE}")

st.markdown("---")

# 2. VISUALISASI
tab1, tab2, tab3 = st.tabs(["📈 Analisis Skor", "👥 Demografi", "📝 Masukan Warga"])

# TAB 1: Analisis Skor
with tab1:
    st.subheader(f"Rata-rata Skor per Aspek (Skala 1 - {int(MAX_SCALE)})")
    if existing_cols and total_resp > 0:
        avg_scores = df_filtered[existing_cols].mean().reset_index()
        avg_scores.columns = ['Kode', 'Skor']
        
        labels = {
            'Q1_Perilaku': 'Perilaku Petugas', 'Q2_Biaya': 'Biaya Pelayanan',
            'Q3_Waktu': 'Waktu Pelayanan', 'Q4_Prosedur': 'Prosedur',
            'Q5_Kesesuaian': 'Kesesuaian Syarat', 'Q6_Kemampuan': 'Kompetensi Petugas',
            'Q7_Pengaduan': 'Penanganan Aduan', 'Q8_Maklumat': 'Maklumat Layanan',
            'Q9_Rating_Total': 'Rating Umum'
        }
        avg_scores['Aspek'] = avg_scores['Kode'].map(labels).fillna(avg_scores['Kode'])
        avg_scores = avg_scores.sort_values('Skor', ascending=True)

        # Bar Chart dengan Range X diperbarui
        fig_scores = px.bar(
            avg_scores, x='Skor', y='Aspek', orientation='h',
            text_auto='.2f', color='Skor', color_continuous_scale='RdYlGn',
            range_x=[0, MAX_SCALE + 0.5] # Agar bar nilai 5 tidak mentok
        )
        st.plotly_chart(fig_scores, use_container_width=True)
        st.caption(f"Keterangan: Skor semakin mendekati {int(MAX_SCALE)} artinya semakin baik.")
    else:
        st.info("Data belum tersedia.")

# TAB 2: Demografi
with tab2:
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        if 'Jenis Kelamin' in df_filtered.columns:
            st.subheader("Jenis Kelamin")
            fig_gender = px.pie(df_filtered, names='Jenis Kelamin', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_gender, use_container_width=True)
    with col_d2:
        if 'Pendidikan' in df_filtered.columns:
            st.subheader("Pendidikan")
            edu_counts = df_filtered['Pendidikan'].value_counts().reset_index()
            edu_counts.columns = ['Pendidikan', 'Jumlah']
            fig_edu = px.bar(edu_counts, x='Pendidikan', y='Jumlah', color='Jumlah')
            st.plotly_chart(fig_edu, use_container_width=True)
            
    if 'Pekerjaan' in df_filtered.columns:
        st.subheader("Profesi / Pekerjaan")
        job_counts = df_filtered['Pekerjaan'].value_counts().reset_index()
        job_counts.columns = ['Pekerjaan', 'Jumlah']
        fig_job = px.bar(job_counts, x='Jumlah', y='Pekerjaan', orientation='h', color='Jumlah', text_auto=True)
        fig_job.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_job, use_container_width=True)

# TAB 3: Feedback
with tab3:
    st.subheader("💬 Kritik & Saran")
    req_cols = ['Timestamp', 'Nama', 'Pekerjaan', 'Feedback', 'Bukti']
    avail_cols = [c for c in req_cols if c in df_filtered.columns]
    
    if 'Feedback' in avail_cols:
        fb_data = df_filtered[avail_cols].dropna(subset=['Feedback'])
        if not fb_data.empty:
            for idx, row in fb_data.iterrows():
                nama = row.get('Nama', 'Anonim')
                pekerjaan = row.get('Pekerjaan', '-')
                waktu = row.get('Timestamp', '-')
                with st.expander(f"📢 {nama} ({pekerjaan})"):
                    st.caption(f"📅 {waktu}")
                    st.info(row['Feedback'])
                    if 'Bukti' in row and pd.notna(row['Bukti']):
                        st.markdown(f"[📎 Lihat Bukti]({row['Bukti']})")
        else:
            st.write("Belum ada data feedback.")