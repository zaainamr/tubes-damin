import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import OrdinalEncoder, StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, silhouette_score, classification_report
)
import kagglehub
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Job Salary Prediction Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD DATA
# ============================================================================
@st.cache_data
def load_dataset():
    """Download dataset dari Kaggle menggunakan kagglehub"""
    try:
        path = kagglehub.dataset_download("nalisha/job-salary-prediction-dataset")
        df = pd.read_csv(os.path.join(path, 'job_salary_prediction_dataset.csv'))
        return df
    except Exception as e:
        st.error(f"Gagal memuat dataset: {e}")
        st.info("Menggunakan data simulasi sebagai alternatif...")
        return create_dummy_data()

def create_dummy_data():
    """Buat data dummy untuk testing jika koneksi gagal"""
    np.random.seed(42)
    n_samples = 1000
    return pd.DataFrame({
        'job_title': np.random.choice(['Data Analyst', 'Data Scientist', 'Software Engineer', 'ML Engineer'], n_samples),
        'experience_years': np.random.randint(0, 21, n_samples),
        'education_level': np.random.choice(['High School', 'Diploma', 'Bachelor', 'Master', 'PhD'], n_samples),
        'skills_count': np.random.randint(1, 20, n_samples),
        'industry': np.random.choice(['Tech', 'Finance', 'Healthcare'], n_samples),
        'company_size': np.random.choice(['Startup', 'Small', 'Medium', 'Large', 'Enterprise'], n_samples),
        'location': np.random.choice(['Jakarta', 'Bandung', 'Surabaya'], n_samples),
        'remote_work': np.random.choice(['Yes', 'No', 'Hybrid'], n_samples),
        'certifications': np.random.randint(0, 6, n_samples),
        'salary': np.random.randint(30000, 150000, n_samples),
    })

# Load data
df = load_dataset()

# ============================================================================
# DATA PREPARATION FUNCTIONS
# ============================================================================
@st.cache_data
def prepare_data(df_input):
    """Persiapan data: encoding dan scaling"""
    df_prep = df_input.copy()
    
    # Ordinal Encoding
    education_order = ['High School', 'Diploma', 'Bachelor', 'Master', 'PhD']
    company_size_order = ['Startup', 'Small', 'Medium', 'Large', 'Enterprise']
    
    ordinal_enc = OrdinalEncoder(categories=[education_order, company_size_order])
    df_prep[['education_level', 'company_size']] = ordinal_enc.fit_transform(
        df_prep[['education_level', 'company_size']]
    )
    
    # One-Hot Encoding
    nominal_cols = ['job_title', 'industry', 'location', 'remote_work']
    df_prep = pd.get_dummies(df_prep, columns=nominal_cols, drop_first=True, dtype=int)
    
    # Feature Scaling
    scaler = StandardScaler()
    numerical_cols = ['experience_years', 'skills_count', 'certifications', 'education_level', 'company_size']
    df_prep[numerical_cols] = scaler.fit_transform(df_prep[numerical_cols])
    
    return df_prep, scaler

# ============================================================================
# TRAINING FUNCTIONS
# ============================================================================
@st.cache_resource
def train_clustering_model(df_prep):
    """Train K-Means clustering model"""
    clustering_vars = ['experience_years', 'skills_count', 'certifications', 'salary']
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_prep[clustering_vars])
    
    # Elbow method & Silhouette score
    silhouette_scores = []
    inertias = []
    k_range = range(2, 11)
    
    np.random.seed(42)
    for k in k_range:
        kmeans_temp = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels_temp = kmeans_temp.fit_predict(X_scaled)
        inertias.append(kmeans_temp.inertia_)
        
        sample_idx = np.random.choice(len(X_scaled), size=min(10000, len(X_scaled)), replace=False)
        silhouette_scores.append(silhouette_score(X_scaled[sample_idx], labels_temp[sample_idx]))
    
    optimal_k = list(k_range)[np.argmax(silhouette_scores)]
    
    # Train final model
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X_scaled)
    
    return kmeans, optimal_k, cluster_labels, X_scaled, silhouette_scores, inertias, clustering_vars

@st.cache_resource
def train_regression_model(df_prep, cluster_labels):
    """Train Linear Regression model"""
    X = df_prep.drop('salary', axis=1)
    y = df_prep['salary']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    metrics = {
        'mae': mean_absolute_error(y_test, y_pred),
        'mse': mean_squared_error(y_test, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
        'r2': r2_score(y_test, y_pred),
        'cv_scores': cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
    }
    
    return model, X_train, X_test, y_train, y_test, y_pred, metrics

@st.cache_resource
def train_classification_model(df_prep, cluster_labels):
    """Train Random Forest Classification model"""
    X = df_prep.drop('salary', axis=1)
    y = cluster_labels
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    model = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, average='weighted'),
        'recall': recall_score(y_test, y_pred, average='weighted'),
        'f1': f1_score(y_test, y_pred, average='weighted'),
        'cv_scores': cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy', n_jobs=-1)
    }
    
    return model, X_train, X_test, y_train, y_test, y_pred, metrics

# ============================================================================
# MAIN APP LOGIC
# ============================================================================
def main():
    st.title("📊 Job Salary Prediction Dashboard")
    st.caption("Aplikasi data mining untuk analisis dan prediksi gaji karyawan dengan K-Means, Linear Regression, dan Random Forest")
    
    # Prepare data
    df_prep, scaler = prepare_data(df)
    
    # Train models
    kmeans, optimal_k, cluster_labels, X_scaled, sil_scores, inertias, clustering_vars = train_clustering_model(df_prep)
    reg_model, X_train_reg, X_test_reg, y_train_reg, y_test_reg, y_pred_reg, reg_metrics = train_regression_model(df_prep, cluster_labels)
    clf_model, X_train_clf, X_test_clf, y_train_clf, y_test_clf, y_pred_clf, clf_metrics = train_classification_model(df_prep, cluster_labels)
    
    # Sidebar menu
    menu = st.sidebar.radio(
        "Pilih Halaman:",
        ["Beranda", "Data Understanding", "Data Preparation", "Data Modeling & Evaluation"]
    )
    
    if menu == "Beranda":
        show_home(df)
    
    elif menu == "Data Understanding":
        show_data_understanding(df)
    
    elif menu == "Data Preparation":
        show_data_preparation(df)
    
    elif menu == "Data Modeling & Evaluation":
        show_modeling_evaluation(
            df, df_prep, kmeans, optimal_k, cluster_labels, X_scaled, sil_scores, inertias,
            reg_model, X_test_reg, y_test_reg, y_pred_reg, reg_metrics,
            clf_model, X_test_clf, y_test_clf, y_pred_clf, clf_metrics
        )

# ============================================================================
# PAGE: BERANDA
# ============================================================================
def show_home(df):
    st.header("Selamat Datang!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Data", f"{len(df):,}")
    with col2:
        st.metric("Rata-rata Salary", f"${df['salary'].mean():,.0f}")
    with col3:
        st.metric("Median Salary", f"${df['salary'].median():,.0f}")
    
    st.divider()
    
    st.subheader("📈 Deskripsi Singkat")
    st.write("""
    Dashboard ini menyediakan analisis komprehensif tentang prediksi gaji karyawan menggunakan:
    
    - **K-Means Clustering**: Segmentasi karyawan ke dalam kelompok dengan karakteristik serupa
    - **Linear Regression**: Prediksi nilai gaji (kontinu) berdasarkan fitur karyawan
    - **Random Forest Classification**: Klasifikasi karyawan ke dalam kelompok berdasarkan gaji
    
    Navigasi ke menu lain untuk melihat analisis detail!
    """)

# ============================================================================
# PAGE: DATA UNDERSTANDING
# ============================================================================
def show_data_understanding(df):
    st.header("1. Data Understanding")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Preview", "Info Dataset", "Statistik", "Distribusi"])
    
    with tab1:
        st.subheader("Preview Data")
        st.dataframe(df.head(20), use_container_width=True)
    
    with tab2:
        st.subheader("Informasi Dataset")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Jumlah Baris", f"{df.shape[0]:,}")
        col2.metric("Jumlah Kolom", df.shape[1])
        col3.metric("Missing Value", df.isnull().sum().sum())
        col4.metric("Data Duplikat", df.duplicated().sum())
        
        st.subheader("Tipe Data")
        dtype_df = pd.DataFrame({
            'Kolom': df.columns,
            'Tipe Data': df.dtypes.astype(str),
            'Non-Null Count': df.notnull().sum(),
            'Missing': df.isnull().sum()
        })
        st.dataframe(dtype_df, use_container_width=True)
    
    with tab3:
        st.subheader("Statistik Deskriptif")
        numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        st.dataframe(df[numerical_cols].describe().T.round(2), use_container_width=True)
    
    with tab4:
        st.subheader("Distribusi Salary")
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        axes[0].hist(df['salary'], bins=30, color='#4C72B0', edgecolor='black', alpha=0.85)
        axes[0].axvline(df['salary'].mean(), color='red', linestyle='--', linewidth=2, label='Mean')
        axes[0].axvline(df['salary'].median(), color='green', linestyle='--', linewidth=2, label='Median')
        axes[0].set_title('Distribusi Salary', fontweight='bold')
        axes[0].set_xlabel('Salary')
        axes[0].set_ylabel('Frekuensi')
        axes[0].legend()
        
        avg_salary_exp = df.groupby('experience_years')['salary'].mean()
        axes[1].plot(avg_salary_exp.index, avg_salary_exp.values, marker='o', linewidth=2, color='#E91E63')
        axes[1].set_title('Rata-rata Salary per Experience Years', fontweight='bold')
        axes[1].set_xlabel('Experience Years')
        axes[1].set_ylabel('Rata-rata Salary')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)

# ============================================================================
# PAGE: DATA PREPARATION
# ============================================================================
def show_data_preparation(df):
    st.header("2. Data Preparation")
    
    tab1, tab2, tab3 = st.tabs(["Encoding Kategorikal", "Feature Scaling", "Summary"])
    
    with tab1:
        st.subheader("Ordinal & One-Hot Encoding")
        st.write("""
        **Ordinal Encoding** (variabel dengan urutan):
        - Education Level: High School → Diploma → Bachelor → Master → PhD
        - Company Size: Startup → Small → Medium → Large → Enterprise
        
        **One-Hot Encoding** (variabel tanpa urutan):
        - Job Title, Industry, Location, Remote Work
        """)
    
    with tab2:
        st.subheader("Feature Scaling (StandardScaler)")
        st.write("""
        Variabel numerik di-scale menggunakan StandardScaler agar memiliki mean=0 dan std=1.
        Ini penting untuk algoritma yang sensitif terhadap skala data (K-Means, Linear Regression).
        """)
    
    with tab3:
        st.subheader("Summary Persiapan Data")
        st.info("""
        ✓ Encoding kategorikal selesai
        ✓ Feature scaling selesai
        ✓ Data siap untuk modeling
        """)

# ============================================================================
# PAGE: MODELING & EVALUATION
# ============================================================================
def show_modeling_evaluation(df, df_prep, kmeans, optimal_k, cluster_labels, X_scaled, sil_scores, inertias,
                              reg_model, X_test_reg, y_test_reg, y_pred_reg, reg_metrics,
                              clf_model, X_test_clf, y_test_clf, y_pred_clf, clf_metrics):
    st.header("3. Data Modeling & Evaluation")
    
    tab_cluster, tab_reg, tab_clf = st.tabs(["K-Means Clustering", "Linear Regression", "Random Forest Classification"])
    
    # ========== CLUSTERING ==========
    with tab_cluster:
        st.subheader("K-Means Clustering")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Penentuan Jumlah Cluster Optimal**")
            fig, ax = plt.subplots(figsize=(10, 5))
            ax2 = ax.twinx()
            
            ax.plot(range(2, 11), inertias, marker='o', color='#2196F3', linewidth=2, label='Inertia')
            ax2.plot(range(2, 11), sil_scores, marker='s', color='#E91E63', linewidth=2, label='Silhouette Score')
            
            ax.set_xlabel('Jumlah Cluster (k)')
            ax.set_ylabel('Inertia', color='#2196F3')
            ax2.set_ylabel('Silhouette Score', color='#E91E63')
            ax.set_title('Elbow Method & Silhouette Score', fontweight='bold')
            ax.grid(True, alpha=0.3)
            
            st.pyplot(fig, use_container_width=True)
        
        with col2:
            col1_stat, col2_stat = st.columns(2)
            col1_stat.metric("Cluster Optimal", optimal_k)
            col2_stat.metric("Silhouette Score", f"{max(sil_scores):.4f}")
            
            st.write("**Distribusi Cluster**")
            cluster_dist = pd.Series(cluster_labels).value_counts().sort_index()
            fig, ax = plt.subplots(figsize=(8, 5))
            cluster_dist.plot(kind='bar', ax=ax, color=plt.cm.Set2(range(optimal_k)))
            ax.set_title('Distribusi Data per Cluster', fontweight='bold')
            ax.set_xlabel('Cluster')
            ax.set_ylabel('Jumlah Data')
            st.pyplot(fig, use_container_width=True)
        
        # PCA Visualization
        st.write("**Visualisasi Cluster (PCA 2D)**")
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)
        
        np.random.seed(42)
        sample_idx = np.random.choice(len(X_pca), size=5000, replace=False)
        
        fig, ax = plt.subplots(figsize=(10, 7))
        scatter = ax.scatter(X_pca[sample_idx, 0], X_pca[sample_idx, 1], 
                           c=cluster_labels[sample_idx], cmap='viridis', alpha=0.5, s=15)
        plt.colorbar(scatter, label='Cluster')
        ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)')
        ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)')
        ax.set_title('K-Means Clustering Visualization (PCA)', fontweight='bold')
        st.pyplot(fig, use_container_width=True)
    
    # ========== REGRESSION ==========
    with tab_reg:
        st.subheader("Linear Regression - Prediksi Salary")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("R² Score", f"{reg_metrics['r2']:.4f}")
        col2.metric("RMSE", f"${reg_metrics['rmse']:,.0f}")
        col3.metric("MAE", f"${reg_metrics['mae']:,.0f}")
        col4.metric("CV Mean R²", f"{reg_metrics['cv_scores'].mean():.4f}")
        
        # Actual vs Predicted
        col1, col2 = st.columns(2)
        
        with col1:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.scatter(y_test_reg, y_pred_reg, alpha=0.1, s=5)
            min_val = min(y_test_reg.min(), y_pred_reg.min())
            max_val = max(y_test_reg.max(), y_pred_reg.max())
            ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2)
            ax.set_xlabel('Actual Salary')
            ax.set_ylabel('Predicted Salary')
            ax.set_title(f'Actual vs Predicted (R² = {reg_metrics["r2"]:.4f})', fontweight='bold')
            st.pyplot(fig, use_container_width=True)
        
        with col2:
            residuals = y_test_reg.values - y_pred_reg
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.hist(residuals, bins=50, color='#2196F3', edgecolor='black', alpha=0.7)
            ax.axvline(x=0, color='red', linestyle='--', linewidth=2)
            ax.set_xlabel('Residual')
            ax.set_ylabel('Frekuensi')
            ax.set_title('Distribusi Residual', fontweight='bold')
            st.pyplot(fig, use_container_width=True)
    
    # ========== CLASSIFICATION ==========
    with tab_clf:
        st.subheader("Random Forest Classification")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Accuracy", f"{clf_metrics['accuracy']:.4f}")
        col2.metric("Precision", f"{clf_metrics['precision']:.4f}")
        col3.metric("Recall", f"{clf_metrics['recall']:.4f}")
        col4.metric("F1-Score", f"{clf_metrics['f1']:.4f}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig, ax = plt.subplots(figsize=(10, 6))
            cm = confusion_matrix(y_test_clf, y_pred_clf)
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                       xticklabels=[f'Cluster {i}' for i in range(optimal_k)],
                       yticklabels=[f'Cluster {i}' for i in range(optimal_k)])
            ax.set_title('Confusion Matrix', fontweight='bold')
            ax.set_xlabel('Predicted')
            ax.set_ylabel('Actual')
            st.pyplot(fig, use_container_width=True)
        
        with col2:
            st.write("**Classification Report**")
            report_dict = classification_report(y_test_clf, y_pred_clf, output_dict=True)
            report_df = pd.DataFrame(report_dict).transpose()
            st.dataframe(report_df.round(4), use_container_width=True)

if __name__ == '__main__':
    main()
