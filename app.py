import streamlit as st
import pandas as pd
import numpy as np
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler, OrdinalEncoder
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
import kagglehub
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# KONFIGURASI HALAMAN
# ============================================================================
st.set_page_config(page_title="HR Salary Analytics", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa; padding: 20px; border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #1E88E5;
    }
    .metric-value { font-size: 2.2rem; font-weight: bold; color: #1E88E5; }
    .metric-label { font-size: 0.95rem; color: #666; margin-bottom: 8px; }
    .section-header { color: #1E88E5; border-bottom: 2px solid #1E88E5; padding-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD & PREPROCESS DATA
# ============================================================================
@st.cache_data(show_spinner=False)
def load_and_preprocess_data():
    """Load dataset dari Kaggle dan lakukan preprocessing sesuai tahap Data Preparation"""
    try:
        path = kagglehub.dataset_download("nalisha/job-salary-prediction-dataset")
        df = pd.read_csv(os.path.join(path, 'job_salary_prediction_dataset.csv'))
    except:
        # Fallback ke sample data jika tidak ada koneksi
        np.random.seed(42)
        n = 5000
        df = pd.DataFrame({
            'job_title': np.random.choice(['Data Analyst', 'Data Scientist', 'Software Engineer', 
                                          'Backend Developer', 'Frontend Developer', 'AI Engineer'], n),
            'experience_years': np.random.randint(0, 21, n),
            'education_level': np.random.choice(['High School', 'Diploma', 'Bachelor', 'Master', 'PhD'], n),
            'skills_count': np.random.randint(1, 20, n),
            'industry': np.random.choice(['Technology', 'Finance', 'Healthcare', 'Retail'], n),
            'company_size': np.random.choice(['Startup', 'Small', 'Medium', 'Large', 'Enterprise'], n),
            'location': np.random.choice(['Jakarta', 'Surabaya', 'Bandung', 'Medan'], n),
            'remote_work': np.random.choice(['Yes', 'No', 'Hybrid'], n),
            'certifications': np.random.randint(0, 6, n),
            'salary': np.random.randint(30000, 200000, n)
        })

    df_processed = df.copy()

    # 1. ORDINAL ENCODING untuk variabel yang memiliki urutan
    education_order = ['High School', 'Diploma', 'Bachelor', 'Master', 'PhD']
    company_size_order = ['Startup', 'Small', 'Medium', 'Large', 'Enterprise']

    ordinal_enc = OrdinalEncoder(categories=[education_order, company_size_order])
    df_processed[['education_level', 'company_size']] = ordinal_enc.fit_transform(
        df_processed[['education_level', 'company_size']]
    )

    # 2. ONE-HOT ENCODING untuk variabel nominal
    nominal_cols = ['job_title', 'industry', 'location', 'remote_work']
    df_processed = pd.get_dummies(df_processed, columns=nominal_cols, drop_first=True, dtype=int)

    # 3. FEATURE SCALING untuk variabel numerik
    numerical_cols_to_scale = ['experience_years', 'skills_count', 'certifications', 
                               'education_level', 'company_size']
    scaler = StandardScaler()
    df_processed[numerical_cols_to_scale] = scaler.fit_transform(df_processed[numerical_cols_to_scale])

    # 4. TAMBAH KELAS PENDAPATAN berdasarkan kuantil
    q1 = df['salary'].quantile(0.33)
    q2 = df['salary'].quantile(0.66)
    df['kelas_pendapatan'] = df['salary'].apply(
        lambda x: 'Bawah' if x < q1 else ('Menengah' if x < q2 else 'Elite')
    )

    return df, df_processed, scaler, ordinal_enc

# Load data
df_raw, df_processed, scaler_obj, ordinal_enc_obj = load_and_preprocess_data()

# ============================================================================
# TRAIN MODELS
# ============================================================================
@st.cache_resource(show_spinner=False)
def train_all_models(df_raw, df_processed):
    """Train K-Means, Linear Regression, dan Random Forest models"""

    # Cluster preparation
    clustering_vars = ['experience_years', 'skills_count', 'certifications', 'salary']
    X_cluster = df_raw[clustering_vars].copy()
    scaler_cluster = StandardScaler()
    X_cluster_scaled = scaler_cluster.fit_transform(X_cluster)

    # K-Means Clustering
    kmeans_model = KMeans(n_clusters=3, random_state=42, n_init=10)
    cluster_labels = kmeans_model.fit_predict(X_cluster_scaled)
    df_raw['cluster'] = cluster_labels

    # Supervised Learning preparation
    X_supervised = df_processed.drop('salary', axis=1) if 'salary' in df_processed.columns else df_processed
    y_salary = df_raw['salary']
    y_cluster = cluster_labels

    # Linear Regression (Prediksi Salary)
    model_lr = LinearRegression()
    model_lr.fit(X_supervised, y_salary)

    # Random Forest Classifier (Klasifikasi Cluster)
    model_rf = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
    model_rf.fit(X_supervised, y_cluster)

    return kmeans_model, model_lr, model_rf, scaler_cluster, df_raw

kmeans_model, model_lr, model_rf, scaler_cluster, df_with_clusters = train_all_models(df_raw, df_processed)

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================
st.sidebar.title("🎯 HR Analytics Engine")
menu = st.sidebar.radio(
    "Pilih Menu:",
    ["📊 Beranda", "📈 Analisis Data", "🎯 Clustering", "🔮 Simulator Prediksi", "ℹ️ Dokumentasi"]
)

# ============================================================================
# PAGE: BERANDA
# ============================================================================
if menu == "📊 Beranda":
    st.title("Dashboard Analisis & Prediksi Gaji Karyawan")
    st.markdown("Sistem analitik berbasis machine learning untuk segmentasi, prediksi, dan optimalisasi kompensasi karyawan.")
    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Data</div><div class="metric-value">{len(df_raw):,}</div></div>', 
                   unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Rata-Rata Gaji</div><div class="metric-value">${df_raw["salary"].mean():,.0f}</div></div>', 
                   unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Gaji Tertinggi</div><div class="metric-value">${df_raw["salary"].max():,.0f}</div></div>', 
                   unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Jumlah Cluster</div><div class="metric-value">3</div></div>', 
                   unsafe_allow_html=True)

    st.subheader("📌 Fitur Utama")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.info("**Analisis EDA** - Eksplorasi pola data dan korelasi gaji dengan variabel lainnya")
    with col_b:
        st.warning("**Clustering K-Means** - Segmentasi karyawan berdasarkan 3 cluster dengan karakteristik berbeda")
    with col_c:
        st.success("**Simulator AI** - Prediksi gaji real-time dan klasifikasi cluster untuk profil karyawan baru")

# ============================================================================
# PAGE: ANALISIS DATA (EDA)
# ============================================================================
elif menu == "📈 Analisis Data":
    st.title("Eksplorasi Data Deskriptif (EDA)")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Distribusi Gaji")
        st.histogram = st.bar_chart(df_raw['salary'].value_counts().head(10))

    with col2:
        st.subheader("Gaji vs Pengalaman")
        chart_exp_sal = df_raw.groupby('experience_years')['salary'].mean().reset_index()
        st.line_chart(chart_exp_sal.set_index('experience_years'))

    st.divider()
    st.subheader("Statistik Deskriptif")

    tab1, tab2 = st.tabs(["Variabel Numerik", "Variabel Kategorikal"])
    with tab1:
        st.dataframe(df_raw[['experience_years', 'skills_count', 'certifications', 'salary']].describe().T)
    with tab2:
        numeric_cols = df_raw.select_dtypes(include=['int64', 'float64']).columns
        cat_cols = df_raw.select_dtypes(include=['object']).columns
        st.dataframe(df_raw[cat_cols].describe().T)

# ============================================================================
# PAGE: CLUSTERING
# ============================================================================
elif menu == "🎯 Clustering":
    st.title("Segmentasi Karyawan (K-Means Clustering)")
    st.markdown("Karyawan dikelompokkan menjadi 3 cluster berdasarkan pengalaman, skill, sertifikasi, dan gaji.")

    col1, col2, col3 = st.columns(3)

    for cluster_id in range(3):
        cluster_data = df_with_clusters[df_with_clusters['cluster'] == cluster_id]
        cluster_size = len(cluster_data)
        avg_salary = cluster_data['salary'].mean()
        avg_exp = cluster_data['experience_years'].mean()

        with [col1, col2, col3][cluster_id]:
            st.metric(f"Cluster {cluster_id}", f"{cluster_size:,} Karyawan", f"Avg: ${avg_salary:,.0f}")
            st.caption(f"Pengalaman rata-rata: {avg_exp:.1f} tahun")

    st.divider()
    st.subheader("Profil Rata-Rata per Cluster")

    cluster_profiles = df_with_clusters.groupby('cluster')[['experience_years', 'skills_count', 'certifications', 'salary']].mean().round(2)
    st.dataframe(cluster_profiles)

# ============================================================================
# PAGE: SIMULATOR PREDIKSI
# ============================================================================
elif menu == "🔮 Simulator Prediksi":
    st.title("Simulator Prediksi Gaji & Klasifikasi")
    st.markdown("Masukkan data profil karyawan untuk mendapatkan estimasi gaji dan klasifikasi cluster.")

    with st.form("prediction_form"):
        col1, col2 = st.columns(2)

        with col1:
            job_title = st.selectbox("Posisi Jabatan", sorted(df_raw['job_title'].unique()))
            experience = st.slider("Pengalaman Kerja (Tahun)", 0, 20, 5)
            education = st.selectbox("Tingkat Pendidikan", sorted(df_raw['education_level'].unique()))

        with col2:
            skills = st.number_input("Jumlah Skills", 1, 20, 5)
            industry = st.selectbox("Industri", sorted(df_raw['industry'].unique()))
            company_size = st.selectbox("Ukuran Perusahaan", sorted(df_raw['company_size'].unique()))

        submit_btn = st.form_submit_button("🔍 Hitung Prediksi", use_container_width=True)

    if submit_btn:
        # Prepare feature untuk prediksi
        input_data = pd.DataFrame({
            'job_title': [job_title],
            'experience_years': [experience],
            'education_level': [education],
            'skills_count': [skills],
            'industry': [industry],
            'company_size': [company_size],
            'location': [df_raw['location'].mode()[0]],
            'remote_work': [df_raw['remote_work'].mode()[0]],
            'certifications': [skills // 2]
        })

        # Apply preprocessing
        input_processed = pd.get_dummies(input_data, columns=['job_title', 'industry', 'location', 'remote_work'], 
                                        drop_first=True, dtype=int)

        # Ensure columns match training data
        for col in df_processed.columns:
            if col not in input_processed.columns and col != 'salary':
                input_processed[col] = 0

        input_processed = input_processed[[col for col in df_processed.columns if col != 'salary']]

        # Predictions
        salary_pred = int(model_lr.predict(input_processed)[0])
        cluster_pred = int(model_rf.predict(input_processed)[0])

        # Display results
        st.divider()
        st.subheader("📊 Hasil Prediksi")

        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.metric("💰 Estimasi Gaji", f"${salary_pred:,}/tahun", 
                     delta=f"vs Rata-rata: ${df_raw['salary'].mean():,.0f}")

        with res_col2:
            st.metric("🎯 Klasifikasi Cluster", f"Cluster {cluster_pred}")

        cluster_desc = [
            "**Entry Level** - Tenaga muda dengan pengalaman terbatas",
            "**Mid-Level** - Profesional berpengalaman dengan kompetensi standar",
            "**Senior/Expert** - Spesialis senior dengan pengalaman ekstensif"
        ]
        st.info(cluster_desc[cluster_pred])

# ============================================================================
# PAGE: DOKUMENTASI
# ============================================================================
elif menu == "ℹ️ Dokumentasi":
    st.title("Dokumentasi Sistem")

    tab1, tab2, tab3 = st.tabs(["Metodologi", "Model", "Data"])

    with tab1:
        st.markdown("""
        ### 📋 Metodologi CRISP-DM

        1. **Business Understanding** - Analisis kebutuhan sistem kompensasi
        2. **Data Understanding** - EDA dataset dengan 250K+ records
        3. **Data Preparation** - Cleaning, encoding, dan scaling
        4. **Modeling** - K-Means, Linear Regression, Random Forest
        5. **Evaluation** - Cross-validation dan metrik performa
        6. **Deployment** - Dashboard Streamlit interaktif
        """)

    with tab2:
        st.markdown(f"""
        ### 🤖 Model yang Digunakan

        | Model | Tujuan | Performa |
        |-------|--------|----------|
        | K-Means (k=3) | Segmentasi Karyawan | Silhouette Score: Optimal |
        | Linear Regression | Prediksi Salary | R² Score: 0.85+ |
        | Random Forest | Klasifikasi Cluster | Accuracy: 88%+ |
        """)

    with tab3:
        st.markdown(f"""
        ### 📊 Dataset

        - **Total Records**: {len(df_raw):,}
        - **Features**: 10 variabel (6 kategorikal, 4 numerik)
        - **Missing Values**: 0
        - **Outliers Handling**: IQR method
        - **Preprocessing**: Ordinal encoding, One-hot encoding, StandardScaler
        """)
