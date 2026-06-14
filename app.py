import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.cluster import KMeans
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, confusion_matrix, classification_report, roc_curve, auc)
import plotly.graph_objects as go
import kagglehub
import warnings
warnings.filterwarnings('ignore')

def format_currency(usd_value, kurs=16000, mode="Tahunan", currency="IDR"):
    """Konversi USD ke IDR atau format USD ringkas"""
    if mode == "Bulanan":
        usd_value = usd_value / 12
        
    if currency == "USD":
        if usd_value >= 1_000_000:
            return f"${usd_value / 1_000_000:.2f}M"
        elif usd_value >= 1_000:
            return f"${usd_value / 1000:.1f}K"
        else:
            return f"${usd_value:,.0f}"
    else:
        idr = usd_value * kurs
        if idr >= 1_000_000_000:
            return f"Rp {idr / 1_000_000_000:.2f} Miliar"
        elif idr >= 1_000_000:
            return f"Rp {idr / 1_000_000:.1f} Juta"
        else:
            return f"Rp {idr:,.0f}"

# ============================================================================
# KONFIGURASI HALAMAN
# ============================================================================
st.set_page_config(page_title="HR Salary Analytics", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Pengaturan padding absolut untuk mencegah overlap dengan sidebar toggle bawaan Streamlit */
    div.block-container {
        padding-top: 4rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
    }
    section[data-testid="stSidebar"] > div {
        padding-top: 4rem !important;
    }
    
    /* Reset padding bawaan pada konten sidebar untuk memastikan alignment sejajar */
    [data-testid="stSidebarUserContent"] {
        padding-top: 0 !important;
    }
    
    /* Pengaturan font global */
    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Styling ukuran dan hierarki warna untuk Heading 1 */
    h1, .stHeadingContainer h1, div[data-testid="stMarkdownContainer"] > h1 { 
        font-size: 2.5rem !important; 
        font-weight: 800 !important; 
        color: #2b3674 !important;
        margin-top: 0 !important;
        padding-top: 0 !important;
        margin-bottom: 0.5rem !important; 
        line-height: 1.2 !important;
        letter-spacing: -0.5px !important;
    }
    
    h2 { font-size: 1.5rem !important; font-weight: 700 !important; color: #2b3674 !important; margin-top: 1.5rem !important; margin-bottom: 0.75rem !important; letter-spacing: -0.5px; }
    h3 { font-size: 1.15rem !important; font-weight: 600 !important; color: #2b3674 !important; margin-top: 1.25rem !important; margin-bottom: 0.5rem !important; }
    p, li, span, div { font-size: 1rem; line-height: 1.5; color: #64748b; }
    
    /* Styling garis pemisah (Divider) */
    hr { margin-top: 1.5rem !important; margin-bottom: 1.5rem !important; border-color: #e2e8f0; }
    
    /* Styling desain komponen Metric Card */
    .metric-card {
        background-color: #ffffff; 
        padding: 1.25rem; 
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1); 
        border-left: 4px solid #1E88E5;
        border-top: 1px solid #eef2f6;
        border-right: 1px solid #eef2f6;
        border-bottom: 1px solid #eef2f6;
        margin-bottom: 1rem;
    }
    .metric-value { font-size: 2.25rem !important; font-weight: 700 !important; color: #1E88E5; line-height: 1.2 !important; }
    .metric-label { font-size: 0.875rem !important; color: #64748b; margin-bottom: 0.5rem !important; font-weight: 600 !important; text-transform: uppercase; letter-spacing: 0.5px; }
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

    # Kelas Pendapatan dihapus agar klasifikasi murni memprediksi hasil K-Means (Cluster) sesuai BAB 1

    return df, df_processed, scaler, ordinal_enc

# Load data
df_raw, df_processed, scaler_obj, ordinal_enc_obj = load_and_preprocess_data()

# Kolom numerik yang menggunakan StandardScaler — dipakai di tab_single & tab_batch
NUMERICAL_COLS_TO_SCALE = ['experience_years', 'skills_count', 'certifications',
                           'education_level', 'company_size']

# ============================================================================
# TRAIN MODELS
# ============================================================================
@st.cache_resource(show_spinner=False)
def train_all_models(_df_raw, _df_processed):
    """Train semua model: K-Means, Linear Regression, Random Forest, Logistic Regression, Naïve Bayes"""

    df_raw_local = _df_raw.copy()
    df_proc_local = _df_processed.copy()

    # ========== UNSUPERVISED: K-Means Clustering ==========
    clustering_vars = ['experience_years', 'skills_count', 'certifications', 'salary']
    X_cluster = df_raw_local[clustering_vars].copy()
    scaler_cluster = StandardScaler()
    X_cluster_scaled = scaler_cluster.fit_transform(X_cluster)

    kmeans_model = KMeans(n_clusters=2, random_state=42, n_init=10)
    cluster_labels = kmeans_model.fit_predict(X_cluster_scaled)
    df_raw_local['cluster'] = cluster_labels

    # ========== PREPARE SUPERVISED FEATURES ==========
    X_supervised = df_proc_local.drop('salary', axis=1) if 'salary' in df_proc_local.columns else df_proc_local
    y_salary = df_raw_local['salary']
    # Target Classification adalah hasil Clustering!
    y_cluster = cluster_labels

    # ========== TRAIN/TEST SPLIT (80/20) ==========
    indices = np.arange(len(X_supervised))
    train_idx, test_idx = train_test_split(
        indices, test_size=0.2, random_state=42, stratify=y_cluster
    )

    X_train, X_test = X_supervised.iloc[train_idx], X_supervised.iloc[test_idx]
    y_train_cluster, y_test_cluster = y_cluster[train_idx], y_cluster[test_idx]
    y_train_salary, y_test_salary = y_salary.iloc[train_idx], y_salary.iloc[test_idx]

    # ========== MODEL 1: Linear Regression (Prediksi Salary) ==========
    model_lr_regress = LinearRegression()
    model_lr_regress.fit(X_train, y_train_salary)
    lr_r2_train = model_lr_regress.score(X_train, y_train_salary)
    lr_r2_test = model_lr_regress.score(X_test, y_test_salary)

    # ========== MODEL 2: Random Forest (Klasifikasi Cluster - existing) ==========
    model_rf_cluster = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
    model_rf_cluster.fit(X_train, y_train_cluster)

    # ========== MODEL 3 (RUBRIK): Logistic Regression (Klasifikasi Cluster) ==========
    model_logreg = LogisticRegression(max_iter=1000, random_state=42, solver='lbfgs')
    model_logreg.fit(X_train, y_train_cluster)

    # ========== MODEL 4 (RUBRIK): Naïve Bayes (Klasifikasi Cluster) ==========
    model_nb = GaussianNB()
    model_nb.fit(X_train, y_train_cluster)

    # ========== EVALUASI SEMUA MODEL KLASIFIKASI ==========
    clf_models = {
        'Logistic Regression': model_logreg,
        'Naïve Bayes': model_nb,
        'Random Forest': model_rf_cluster
    }

    metrics = {}
    conf_matrices = {}
    class_reports = {}
    for name, model in clf_models.items():
        y_pred = model.predict(X_test)
        metrics[name] = {
            'Accuracy': accuracy_score(y_test_cluster, y_pred),
            'Precision': precision_score(y_test_cluster, y_pred, average='weighted', zero_division=0),
            'Recall': recall_score(y_test_cluster, y_pred, average='weighted', zero_division=0),
            'F1-Score': f1_score(y_test_cluster, y_pred, average='weighted', zero_division=0)
        }
        conf_matrices[name] = confusion_matrix(y_test_cluster, y_pred)
        class_reports[name] = classification_report(
            y_test_cluster, y_pred, output_dict=True
        )

    # Calculate ROC Data for Supervised Evaluation
    roc_data = {}
    for name, model in clf_models.items():
        if hasattr(model, "predict_proba"):
            y_prob = model.predict_proba(X_test)[:, 1]
            fpr, tpr, _ = roc_curve(y_test_cluster, y_prob)
            roc_data[name] = {'fpr': fpr, 'tpr': tpr, 'auc': auc(fpr, tpr)}

    # Calculate Elbow Data for Unsupervised Evaluation
    elbow_inertia = []
    for k in range(1, 9):
        km = KMeans(n_clusters=k, random_state=42, n_init=5)
        km.fit(X_cluster_scaled)
        elbow_inertia.append(km.inertia_)

    return {
        'kmeans': kmeans_model, 'scaler_cluster': scaler_cluster,
        'model_lr_regress': model_lr_regress, 'model_rf_cluster': model_rf_cluster,
        'lr_r2_train': lr_r2_train, 'lr_r2_test': lr_r2_test,
        'model_logreg': model_logreg, 'model_nb': model_nb,
        'metrics': metrics, 'roc_data': roc_data, 'elbow_inertia': elbow_inertia,
        'conf_matrices': conf_matrices, 'class_reports': class_reports,
        'y_test_cluster': y_test_cluster, 'X_test': X_test,
        'train_size': len(train_idx), 'test_size': len(test_idx),
        'df_raw': df_raw_local
    }

results = train_all_models(df_raw, df_processed)

# Unpack results
kmeans_model = results['kmeans']
scaler_cluster = results['scaler_cluster']
model_lr_regress = results['model_lr_regress']
model_rf_cluster = results['model_rf_cluster']
model_logreg = results['model_logreg']
model_nb = results['model_nb']
df_with_clusters = results['df_raw']

# Calculate cluster mapping dynamically
cluster_exp = df_with_clusters.groupby('cluster')['experience_years'].mean().sort_values()
cluster_mapping = {cluster_id: rank for rank, cluster_id in enumerate(cluster_exp.index)}
cluster_names = {
    0: "Junior",
    1: "Senior"
}
# Label urut berdasarkan cluster ID asli (untuk confusion matrix & classification report)
ordered_labels = [cluster_names[cluster_mapping[i]] for i in sorted(cluster_mapping.keys())]

# Remap classification report keys dari angka (0/1) ke label (Junior/Senior)
class_reports_mapped = {}
for model_name, report in results['class_reports'].items():
    mapped = {}
    for key, val in report.items():
        if key in ['0', '1']:
            mapped[cluster_names[cluster_mapping[int(key)]]] = val
        else:
            mapped[key] = val
    class_reports_mapped[model_name] = mapped
results['class_reports'] = class_reports_mapped

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================
from streamlit_option_menu import option_menu

with st.sidebar:
    st.markdown('<h2 style="font-size: 1.75rem; font-weight: 800; margin-top: 0; margin-bottom: 1.5rem; color: #1E88E5; line-height: 1.2;">HR Analytics<br>Engine</h2>', unsafe_allow_html=True)
    menu = option_menu(
        menu_title=None,
        options=["Beranda", "Analisis Data", "Clustering", "Perbandingan Model", "Simulator Prediksi", "Dokumentasi"],
        icons=["house", "bar-chart-line", "diagram-3", "graph-up", "cpu", "info-circle"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "inherit", "font-size": "1.1rem"},
            "nav-link": {
                "font-size": "0.95rem", "font-weight": "500", "text-align": "left", 
                "margin": "0.2rem 0", "padding": "0.75rem 1rem", "border-radius": "12px", "color": "#64748b"
            },
            "nav-link-selected": {
                "background-color": "#1E88E5", "color": "white", "font-weight": "600",
                "box-shadow": "0px 4px 10px rgba(30, 136, 229, 0.3)"
            },
        }
    )

    st.divider()
    st.markdown("⚙️ **Pengaturan Konversi Gaji**")
    global_currency = st.radio("Mata Uang:", ["IDR (Rupiah)", "USD (Asli)"], horizontal=True)
    global_currency_arg = "IDR" if global_currency == "IDR (Rupiah)" else "USD"
    
    if global_currency_arg == "IDR":
        global_kurs = st.number_input("Kurs USD ke IDR", min_value=10000, max_value=25000, value=16000, step=500, help="Sesuaikan dengan nilai tukar saat ini")
    else:
        global_kurs = 16000 # dummy value, not used for USD formatting but needed to avoid error
        
    global_periode = st.radio("Tampilkan Gaji sebagai:", ["Tahunan", "Bulanan"], horizontal=True)

# ============================================================================
# PAGE: BERANDA
# ============================================================================
if menu == "Beranda":
    st.title("Dashboard Analisis & Prediksi Gaji Karyawan")
    st.markdown("Sistem analitik berbasis machine learning untuk segmentasi, prediksi, dan optimalisasi kompensasi karyawan.")
    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Data</div><div class="metric-value">{len(df_raw):,}</div></div>', 
                   unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Rata-Rata Gaji ({global_periode})</div><div class="metric-value">{format_currency(df_raw["salary"].mean(), global_kurs, global_periode, global_currency_arg)}</div></div>', 
                   unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Gaji Tertinggi ({global_periode})</div><div class="metric-value">{format_currency(df_raw["salary"].max(), global_kurs, global_periode, global_currency_arg)}</div></div>', 
                   unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Jumlah Cluster</div><div class="metric-value">2</div></div>', 
                   unsafe_allow_html=True)

    st.subheader("Fitur Utama")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.info("**Analisis EDA** - Eksplorasi pola data dan korelasi gaji dengan variabel lainnya")
    with col_b:
        st.warning("**Clustering K-Means** - Segmentasi karyawan berdasarkan 2 cluster: Junior dan Senior")
    with col_c:
        st.success("**Simulator AI** - Prediksi gaji real-time dan klasifikasi cluster untuk profil karyawan baru")

# ============================================================================
# PAGE: ANALISIS DATA (EDA)
# ============================================================================
elif menu == "Analisis Data":
    st.title("Eksplorasi Data Deskriptif (EDA)")

    st.markdown("Visualisasi interaktif dataset untuk memahami sebaran dan tren data sebelum proses *Machine Learning*.")

    currency_label = "Rupiah" if global_currency_arg == "IDR" else "USD"
    currency_symbol = "Rp" if global_currency_arg == "IDR" else "$"

    # Siapkan DataFrame untuk plotting agar tersinkronisasi dengan konversi Rupiah
    df_plot = df_raw.copy()
    df_plot['Gaji Plot'] = df_plot['salary'] * (global_kurs if global_currency_arg == "IDR" else 1)
    if global_periode == "Bulanan":
        df_plot['Gaji Plot'] = df_plot['Gaji Plot'] / 12

    # Baris 1: Histogram dan Line Chart
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Distribusi Gaji Keseluruhan")
        fig_hist = px.histogram(df_plot, x='Gaji Plot', nbins=30,
                                color_discrete_sequence=['#1E88E5'],
                                title=f"Sebaran Gaji ({global_periode})",
                                opacity=0.8)
        fig_hist.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20),
                               xaxis_title=f"Nominal Gaji ({currency_label})", yaxis_title="Jumlah Karyawan")
        st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        st.subheader("Gaji vs Pengalaman")
        chart_exp_sal = df_plot.groupby('experience_years')['Gaji Plot'].mean().reset_index()
        fig_line = px.line(chart_exp_sal, x='experience_years', y='Gaji Plot', 
                           markers=True, color_discrete_sequence=['#ff9800'],
                           labels={'experience_years': 'Pengalaman (Tahun)', 'Gaji Plot': f'Rata-rata Gaji ({currency_symbol})'},
                           title="Tren Kenaikan Gaji Berdasarkan Pengalaman")
        fig_line.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_line, use_container_width=True)

    # Baris 2: Boxplot dan Donut Chart
    st.divider()
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Gaji Berdasarkan Ukuran Perusahaan")
        fig_box = px.box(df_plot, x='company_size', y='Gaji Plot',
                         color='company_size', color_discrete_sequence=px.colors.qualitative.Set2,
                         title=f"Rentang Gaji per Ukuran Perusahaan")
        fig_box.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20), showlegend=False,
                              xaxis_title="Ukuran Perusahaan", yaxis_title=f"Gaji ({currency_symbol})")
        st.plotly_chart(fig_box, use_container_width=True)
        
    with col4:
        st.subheader("Proporsi Industri")
        fig_pie = px.pie(df_raw, names='industry', hole=0.45,
                         color_discrete_sequence=px.colors.qualitative.Pastel,
                         title="Sebaran Karyawan Berdasarkan Sektor Industri")
        fig_pie.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_pie, use_container_width=True)

    st.divider()
    st.subheader("Korelasi Antar Variabel (Heatmap)")
    st.markdown("Mengukur kekuatan hubungan linier antar variabel numerik. Semakin mendekati 1 (atau -1), semakin kuat hubungannya.")
    
    corr_cols = ['experience_years', 'skills_count', 'certifications', 'salary']
    corr_matrix = df_raw[corr_cols].corr().round(2)
    # Ubah nama kolom agar rapi
    corr_matrix.columns = corr_matrix.columns.str.replace('_', ' ').str.title()
    corr_matrix.index = corr_matrix.index.str.replace('_', ' ').str.title()
    
    fig_corr = px.imshow(corr_matrix, text_auto=True, aspect="auto", 
                         color_continuous_scale='RdBu_r', 
                         title="Heatmap Korelasi Pearson")
    fig_corr.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_corr, use_container_width=True)

    st.divider()
    st.subheader("Statistik Deskriptif")

    tab1, tab2 = st.tabs(["Variabel Numerik", "Variabel Kategorikal"])
    
    def format_index_names(df_to_format):
        df_formatted = df_to_format.copy()
        df_formatted.index = df_formatted.index.str.replace('_', ' ').str.title()
        return df_formatted

    with tab1:
        num_stats = df_raw[['experience_years', 'skills_count', 'certifications', 'salary']].describe().T
        st.dataframe(format_index_names(num_stats))
    with tab2:
        cat_cols = df_raw.select_dtypes(include=['object']).columns
        cat_stats = df_raw[cat_cols].describe().T
        st.dataframe(format_index_names(cat_stats))

# ============================================================================
# PAGE: CLUSTERING
# ============================================================================
elif menu == "Clustering":
    st.title("Segmentasi Karyawan (K-Means Clustering)")
    st.markdown("Karyawan dikelompokkan menjadi **2 cluster** (Junior & Senior) berdasarkan pengalaman, skill, sertifikasi, dan gaji.")

    col1, col2 = st.columns(2)

    # Sort the cluster IDs by experience (rank 0=Junior, 1=Senior)
    sorted_cluster_ids = list(cluster_exp.index)

    for rank, cluster_id in enumerate(sorted_cluster_ids):
        cluster_data = df_with_clusters[df_with_clusters['cluster'] == cluster_id]
        cluster_size = len(cluster_data)
        avg_salary = cluster_data['salary'].mean()
        avg_exp = cluster_data['experience_years'].mean()

        with [col1, col2][rank]:
            st.metric(cluster_names[rank], f"{cluster_size:,} Karyawan", f"Avg: {format_currency(avg_salary, global_kurs, global_periode, global_currency_arg)}", help=f"Karyawan di kelas {cluster_names[rank]}")
            st.caption(f"Pengalaman rata-rata: {avg_exp:.1f} tahun")

    st.divider()
    st.subheader("Evaluasi K-Means: Elbow Method")
    st.markdown("Grafik ini membuktikan secara matematis mengapa kita memilih **K=2** (Junior & Senior). Siku (*elbow*) yang terbentuk pada K=2 menunjukkan bahwa penambahan cluster ketiga tidak lagi memberikan penurunan *error* (Inertia) yang signifikan.")
    
    elbow_df = pd.DataFrame({'K': range(1, 9), 'Inertia': results['elbow_inertia']})
    fig_elbow = px.line(elbow_df, x='K', y='Inertia', markers=True, 
                        title="Metode Elbow untuk Optimasi Jumlah Cluster")
    # Add vertical line at K=2
    fig_elbow.add_vline(x=2, line_dash="dash", line_color="red", annotation_text="Titik Siku (K=2)")
    fig_elbow.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_elbow, use_container_width=True)

    st.divider()
    st.subheader("Visualisasi Cluster Interaktif")
    st.markdown("Scatter plot di bawah menunjukkan bagaimana algoritma memisahkan profil karyawan secara nyata.")
    
    # Map label untuk plotting
    df_plot_cluster = df_with_clusters.copy()
    df_plot_cluster['Level'] = df_plot_cluster['cluster'].map(lambda x: cluster_names[cluster_mapping[x]])
    
    # Sesuaikan Gaji dengan Mata Uang
    currency_symbol = "Rp" if global_currency_arg == "IDR" else "$"
    df_plot_cluster['Gaji Plot'] = df_plot_cluster['salary'] * (global_kurs if global_currency_arg == "IDR" else 1)
    if global_periode == "Bulanan":
        df_plot_cluster['Gaji Plot'] = df_plot_cluster['Gaji Plot'] / 12
        
    # Ambil sample 1000 data agar browser tidak lag saat rendering interaktif
    df_sample = df_plot_cluster.sample(n=min(1000, len(df_plot_cluster)), random_state=42)
        
    fig_cluster = px.scatter(df_sample, x='experience_years', y='Gaji Plot', color='Level',
                             color_discrete_map={"Junior": "#3b82f6", "Senior": "#f59e0b"},
                             hover_data=['skills_count', 'certifications'],
                             labels={'experience_years': 'Pengalaman (Tahun)', 'Gaji Plot': f'Gaji ({currency_symbol})'},
                             title="Sebaran Cluster: Pengalaman vs Gaji (Sample 1000 Data)")
    fig_cluster.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_cluster, use_container_width=True)

    st.divider()
    st.subheader("Profil Rata-Rata per Cluster")

    cluster_profiles = df_with_clusters.groupby('cluster')[['experience_years', 'skills_count', 'certifications', 'salary']].mean().round(2)
    # Map raw cluster ID index to level name
    cluster_profiles['level'] = cluster_profiles.index.map(lambda x: cluster_names[cluster_mapping[x]])
    cluster_profiles = cluster_profiles.set_index('level').loc[["Junior", "Senior"]]
    cluster_profiles.columns = cluster_profiles.columns.str.replace('_', ' ').str.title()
    st.dataframe(cluster_profiles)

# ============================================================================
# PAGE: PERBANDINGAN MODEL
# ============================================================================
elif menu == "Perbandingan Model":
    st.title("Perbandingan Model Klasifikasi")
    st.markdown("""
    Perbandingan performa **Logistic Regression**, **Naïve Bayes**, dan **Random Forest** 
    untuk memprediksi **Cluster Karyawan** (Junior / Senior).
    """)

    st.info(f"Data dibagi **{results['train_size']:,}** train / **{results['test_size']:,}** test (80/20 split, stratified)")

    # --- Tabel Metrics ---
    st.subheader("Tabel Perbandingan Metrik")
    metrics_df = pd.DataFrame(results['metrics']).T
    metrics_df = metrics_df.round(4)

    # Highlight best per column
    st.dataframe(metrics_df.style.highlight_max(axis=0, color='#c8e6c9'), use_container_width=True)

    # --- Bar Chart Comparison ---
    st.subheader("Visualisasi Perbandingan")
    chart_df = metrics_df.reset_index().melt(id_vars='index', var_name='Metric', value_name='Score')
    chart_df.columns = ['Model', 'Metric', 'Score']

    metric_tabs = st.tabs(list(metrics_df.columns))
    for i, metric_name in enumerate(metrics_df.columns):
        with metric_tabs[i]:
            metric_data = metrics_df[[metric_name]].sort_values(metric_name, ascending=False)
            st.bar_chart(metric_data, horizontal=True)
            best_model = metric_data.index[0]
            best_val = metric_data.iloc[0, 0]
            st.success(f"**{best_model}** unggul di {metric_name} dengan skor **{best_val:.4f}**")

    # --- Confusion Matrix ---
    st.divider()
    st.subheader("Confusion Matrix")
    cm_cols = st.columns(3)
    for idx, (name, cm) in enumerate(results['conf_matrices'].items()):
        with cm_cols[idx]:
            st.markdown(f"**{name}**")
            fig, ax = plt.subplots(figsize=(4, 3))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                        xticklabels=ordered_labels, 
                        yticklabels=ordered_labels,
                        cbar=False, ax=ax)
            ax.set_xlabel('Prediksi')
            ax.set_ylabel('Aktual')
            st.pyplot(fig, use_container_width=True)
    st.caption("Catatan: Distribusi diagonal utama merepresentasikan tingkat akurasi prediksi (*True Positives/Negatives*), sedangkan sel lainnya menunjukkan tingkat misklasifikasi.")

    # --- Per-Class Report ---
    st.divider()
    st.subheader("Laporan Per-Kelas")
    report_model = st.selectbox("Pilih model:", list(results['class_reports'].keys()))
    report = results['class_reports'][report_model]
    report_df = pd.DataFrame({
        k: v for k, v in report.items()
        if k in ordered_labels
    }).T.round(4)
    st.dataframe(report_df, use_container_width=True)

    # --- Feature Importance ---
    st.divider()
    st.subheader("Faktor Penentu (Feature Importance)")
    st.markdown("Analisis seberapa besar pengaruh setiap atribut data terhadap penentuan level karyawan (berdasarkan bobot dari *Random Forest*).")
    
    rf_model = results['model_rf_cluster']
    feature_names = results['X_test'].columns.str.replace('_', ' ').str.title()
    importances = rf_model.feature_importances_
    
    feat_df = pd.DataFrame({
        'Atribut': feature_names,
        'Tingkat Pengaruh': importances
    }).sort_values('Tingkat Pengaruh', ascending=True).tail(10) # Top 10
    
    fig_feat = px.bar(feat_df, x='Tingkat Pengaruh', y='Atribut', orientation='h',
                      title="Top 10 Atribut Paling Berpengaruh",
                      color='Tingkat Pengaruh', color_continuous_scale='Blues')
    fig_feat.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
    st.plotly_chart(fig_feat, use_container_width=True)
    st.caption("Catatan: Atribut dengan nilai importance tertinggi memiliki kontribusi paling signifikan dalam pembentukan pola keputusan (*decision boundaries*) pada model.")

    # --- ROC Curve ---
    st.divider()
    st.subheader("Kurva ROC & AUC (Evaluasi Supervised)")
    st.markdown("Kurva ROC (*Receiver Operating Characteristic*) menunjukkan seberapa kuat model membedakan kelas Junior dan Senior. Semakin kurva mendekati sudut kiri atas (AUC mendekati 1.0), semakin sempurna model tersebut.")
    
    fig_roc = go.Figure()
    for name, data in results['roc_data'].items():
        fig_roc.add_trace(go.Scatter(x=data['fpr'], y=data['tpr'], mode='lines', 
                                     name=f"{name} (AUC = {data['auc']:.2f})"))
    
    # Add random guess line
    fig_roc.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines', line=dict(dash='dash', color='grey'), name='Tebakan Acak'))
    fig_roc.update_layout(title="ROC Curve - Perbandingan Model Klasifikasi", 
                          xaxis_title="False Positive Rate", yaxis_title="True Positive Rate",
                          template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_roc, use_container_width=True)
    st.caption("Catatan: Kurva yang mendekati sudut kiri atas mengindikasikan rasio klasifikasi benar (*TPR*) yang tinggi dengan error (*FPR*) yang rendah. Garis putus-putus adalah batas tebakan acak (AUC=0.50).")

    # --- Kesimpulan ---
    st.divider()
    st.subheader("Kesimpulan")
    best_by_f1 = max(results['metrics'].items(), key=lambda x: x[1]['F1-Score'])
    best_by_acc = max(results['metrics'].items(), key=lambda x: x[1]['Accuracy'])
    st.markdown(f"""
    - **Model terbaik berdasarkan Accuracy**: **{best_by_acc[0]}** ({best_by_acc[1]['Accuracy']:.4f})
    - **Model terbaik berdasarkan F1-Score**: **{best_by_f1[0]}** ({best_by_f1[1]['F1-Score']:.4f})
    """)
    st.info("**F1-Score** umumnya lebih reliable untuk evaluasi karena mempertimbangkan keseimbangan antara Precision dan Recall, terutama pada dataset yang tidak seimbang.")

# ============================================================================
# PAGE: SIMULATOR PREDIKSI
# ============================================================================
elif menu == "Simulator Prediksi":
    st.title("Simulator Prediksi Gaji & Klasifikasi")
    st.markdown("Masukkan data profil karyawan untuk mendapatkan estimasi gaji dan klasifikasi.")

    tab_single, tab_batch = st.tabs(["Prediksi Tunggal", "Prediksi Massal (Upload CSV)"])

    with tab_single:
        with st.form("prediction_form"):
            col1, col2 = st.columns(2)

            with col1:
                job_title = st.selectbox("Posisi Jabatan", sorted(df_raw['job_title'].unique()), help="Pilih peran atau jabatan pekerjaan.")
                experience = st.slider("Pengalaman Kerja (Tahun)", 0, 20, 5, help="Total tahun pengalaman kerja profesional.")
                education = st.selectbox("Tingkat Pendidikan", ['High School', 'Diploma', 'Bachelor', 'Master', 'PhD'], help="Pendidikan formal tertinggi yang dicapai.")

            with col2:
                skills = st.number_input("Jumlah Skills", 1, 20, 5, help="Jumlah keahlian teknis (tools/bahasa pemrograman) yang dikuasai.")
                certifications = st.number_input("Jumlah Sertifikasi", 0, 10, 1, help="Total sertifikasi profesional yang dimiliki.")
                industry = st.selectbox("Industri", sorted(df_raw['industry'].unique()), help="Sektor industri tempat perusahaan beroperasi.")
                company_size = st.selectbox("Ukuran Perusahaan", ['Startup', 'Small', 'Medium', 'Large', 'Enterprise'], help="Kategori ukuran perusahaan.")

            clf_choice = st.selectbox(
                "Model Klasifikasi Level Karyawan",
                ["Bandingkan Semua", "Logistic Regression", "Naïve Bayes", "Random Forest"],
                help="Pilih model Machine Learning untuk memprediksi cluster (Junior/Senior)."
            )

            submit_btn = st.form_submit_button("Hitung Prediksi", use_container_width=True)

        if submit_btn:
            with st.spinner("Memproses prediksi model Machine Learning..."):
                time.sleep(1.2)

                # Prepare feature
            input_data = pd.DataFrame({
                'job_title': [job_title],
                'experience_years': [experience],
                'education_level': [education],
                'skills_count': [skills],
                'certifications': [certifications],
                'industry': [industry],
                'company_size': [company_size],
                'location': [df_raw['location'].mode()[0]],
                'remote_work': [df_raw['remote_work'].mode()[0]]
            })

            # Preprocessing
            input_data[['education_level', 'company_size']] = ordinal_enc_obj.transform(
                input_data[['education_level', 'company_size']]
            )

            input_data[NUMERICAL_COLS_TO_SCALE] = scaler_obj.transform(input_data[NUMERICAL_COLS_TO_SCALE])

            input_processed = pd.get_dummies(input_data, columns=['job_title', 'industry', 'location', 'remote_work'],
                                            drop_first=True, dtype=int)

            for col in df_processed.columns:
                if col not in input_processed.columns and col != 'salary':
                    input_processed[col] = 0
            input_processed = input_processed[[col for col in df_processed.columns if col != 'salary']]

            # === Predictions ===
            salary_pred = int(model_lr_regress.predict(input_processed)[0])
            cluster_pred = int(model_rf_cluster.predict(input_processed)[0])

            st.divider()
            st.subheader("Hasil Prediksi")

            # Row 1: Salary + Cluster
            res_col1, res_col2 = st.columns(2)
            with res_col1:
                avg_salary_idr = df_raw['salary'].mean()
                delta_val = salary_pred - avg_salary_idr
                delta_str = f"vs Rata-rata: {format_currency(delta_val, global_kurs, global_periode, global_currency_arg)}" if delta_val > 0 else f"vs Rata-rata: -{format_currency(abs(delta_val), global_kurs, global_periode, global_currency_arg)}"
                st.metric(f"Estimasi Gaji ({global_periode})", format_currency(salary_pred, global_kurs, global_periode, global_currency_arg),
                         delta=delta_str, help="Prediksi gaji berdasarkan model Linear Regression.")
            with res_col2:
                rank = cluster_mapping[cluster_pred]
                st.metric("Level Karyawan (K-Means + RF)", cluster_names[rank], help="Segmentasi profil karyawan berdasarkan model klasifikasi Random Forest atas K-Means clustering.")

            # Row 2: Classification Details
            st.divider()
            st.subheader("Prediksi Klasifikasi Cluster (Supervised Learning)")

            clf_models_map = {
                'Logistic Regression': model_logreg,
                'Naïve Bayes': model_nb,
                'Random Forest': model_rf_cluster
            }

            if clf_choice == "Bandingkan Semua":
                comp_cols = st.columns(3)
                for idx, (name, model) in enumerate(clf_models_map.items()):
                    pred_cluster = model.predict(input_processed)[0]
                    rank = cluster_mapping[pred_cluster]
                    pred_label = cluster_names[rank]
                    with comp_cols[idx]:
                        st.metric(name, pred_label)
            else:
                model_selected = clf_models_map[clf_choice]
                pred_cluster = model_selected.predict(input_processed)[0]
                rank = cluster_mapping[pred_cluster]
                pred_label = cluster_names[rank]
                st.metric(f"Prediksi ({clf_choice})", pred_label)


            st.divider()
            st.markdown("⬇️ **Simpan Hasil**")
            csv_data = pd.DataFrame({
                "Job Title": [job_title], "Experience": [experience], "Education": [education],
                "Skills": [skills], "Industry": [industry], "Company Size": [company_size],
                "Prediksi Gaji": [salary_pred], "Level": [cluster_names[cluster_mapping[cluster_pred]]]
            }).to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Hasil Prediksi (CSV)",
                data=csv_data,
                file_name="prediksi_gaji_tunggal.csv",
                mime="text/csv",
            )

    with tab_batch:
        st.subheader("Upload Data Karyawan")
        st.markdown("Unggah file CSV yang berisi sekumpulan data calon karyawan.")
        st.info("Format kolom yang wajib ada: `job_title`, `experience_years`, `education_level`, `skills_count`, `certifications`, `industry`, `company_size`. Kolom lain akan diisi otomatis menggunakan data modus (mayoritas).")
        
        uploaded_file = st.file_uploader("Pilih file CSV", type=["csv"])
        if uploaded_file is not None:
            try:
                batch_df = pd.read_csv(uploaded_file)
                st.write("Preview Data yang Diunggah:")
                st.dataframe(batch_df.head(), use_container_width=True)
                
                if st.button("Proses Prediksi Massal", use_container_width=True):
                    with st.spinner("Memproses seluruh baris data menggunakan model Machine Learning..."):
                        import time
                        time.sleep(1.5)
                        
                        batch_input = batch_df.copy()
                        # Missing columns
                        if 'location' not in batch_input: batch_input['location'] = df_raw['location'].mode()[0]
                        if 'remote_work' not in batch_input: batch_input['remote_work'] = df_raw['remote_work'].mode()[0]
                        if 'certifications' not in batch_input: batch_input['certifications'] = batch_input['skills_count'] // 2 # Fallback
                        
                        # Encode
                        batch_input[['education_level', 'company_size']] = ordinal_enc_obj.transform(
                            batch_input[['education_level', 'company_size']]
                        )
                        batch_input[NUMERICAL_COLS_TO_SCALE] = scaler_obj.transform(batch_input[NUMERICAL_COLS_TO_SCALE])
                        
                        # Dummies
                        batch_processed = pd.get_dummies(batch_input, columns=['job_title', 'industry', 'location', 'remote_work'], drop_first=True, dtype=int)
                        
                        # Align columns with training data
                        for col in df_processed.columns:
                            if col not in batch_processed.columns and col != 'salary':
                                batch_processed[col] = 0
                        batch_processed = batch_processed[[col for col in df_processed.columns if col != 'salary']]
                        
                        # Predict
                        batch_salary_pred = model_lr_regress.predict(batch_processed)
                        batch_cluster_pred = model_rf_cluster.predict(batch_processed)
                        
                        # Format output
                        batch_df['Estimasi Gaji'] = [format_currency(val, global_kurs, global_periode, global_currency_arg) for val in batch_salary_pred]
                        batch_df['Level Prediksi'] = [cluster_names[cluster_mapping[int(c)]] for c in batch_cluster_pred]
                        
                        st.success(f"Prediksi massal untuk {len(batch_df)} karyawan berhasil diselesaikan!")
                        st.dataframe(batch_df, use_container_width=True)
                        
                        st.divider()
                        csv_batch = batch_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Download Laporan Massal (CSV)",
                            data=csv_batch,
                            file_name="prediksi_gaji_massal.csv",
                            mime="text/csv",
                        )
                        
            except Exception as e:
                st.error(f"Gagal memproses file. Pastikan format nama kolom sesuai dengan ketentuan. (Error details: {e})")

# ============================================================================
# PAGE: DOKUMENTASI
# ============================================================================
elif menu == "Dokumentasi":
    st.title("Dokumentasi Sistem")

    tab1, tab2, tab3 = st.tabs(["Metodologi", "Model", "Data"])

    with tab1:
        st.markdown("""
        ### Metodologi CRISP-DM

        1. **Business Understanding** - Analisis kebutuhan sistem kompensasi
        2. **Data Understanding** - EDA dataset dengan 250K+ records
        3. **Data Preparation** - Cleaning, encoding, dan scaling
        4. **Modeling** - K-Means, Logistic Regression, Naïve Bayes, Linear Regression, Random Forest
        5. **Evaluation** - Train/test split 80/20 dan metrik performa
        6. **Deployment** - Dashboard Streamlit interaktif
        """)

    with tab2:
        lr_r2 = results['lr_r2_test']
        m = results['metrics']
        st.markdown(f"""
        ### Model yang Digunakan

        #### Unsupervised Learning
        | Model | Tujuan | Keterangan |
        |-------|--------|------------|
        | K-Means (k=2) | Segmentasi Karyawan | Cluster: Junior & Senior |

        #### Supervised Learning — Sesuai Rubrik
        | Model | Tujuan | Accuracy | F1-Score |
        |-------|--------|----------|----------|
        | Logistic Regression | Klasifikasi Cluster Karyawan | {m['Logistic Regression']['Accuracy']:.4f} | {m['Logistic Regression']['F1-Score']:.4f} |
        | Naïve Bayes | Klasifikasi Cluster Karyawan | {m['Naïve Bayes']['Accuracy']:.4f} | {m['Naïve Bayes']['F1-Score']:.4f} |

        #### Supervised Learning — Tambahan (Perbandingan)
        | Model | Tujuan | Performa |
        |-------|--------|----------|
        | Linear Regression | Prediksi Salary | R² Score: {lr_r2:.4f} |
        | Random Forest | Klasifikasi Cluster Karyawan | Accuracy: {m['Random Forest']['Accuracy']:.4f} |
        """)

    with tab3:
        st.markdown(f"""
        ### Dataset

        - **Total Records**: {len(df_raw):,}
        - **Features**: 10 variabel (6 kategorikal, 4 numerik)
        - **Target Klasifikasi**: `cluster` (Junior / Senior) hasil dari K-Means
        - **Missing Values**: 0
        - **Train/Test Split**: 80/20 (stratified)
        - **Preprocessing**: Ordinal encoding, One-hot encoding, StandardScaler
        """)

