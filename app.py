import os

import kagglehub
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st


DATASET_NAME = "nalisha/job-salary-prediction-dataset"
DATASET_FILE = "job_salary_prediction_dataset.csv"


@st.cache_data(show_spinner="Mengunduh dataset dari Kaggle...", ttl=86400)
def get_dataset_path():
    """Download dataset public dari Kaggle dan kembalikan path file CSV."""
    path = kagglehub.dataset_download(DATASET_NAME)
    return os.path.join(path, DATASET_FILE)


def summarize_dataframe(df: pd.DataFrame):
    """Menghasilkan ringkasan utama dataset untuk dashboard."""
    numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

    missing = df.isnull().sum()
    duplicate_count = int(df.duplicated().sum())

    summary = {
        "Jumlah baris": int(df.shape[0]),
        "Jumlah kolom": int(df.shape[1]),
        "Kolom numerik": len(numerical_cols),
        "Kolom kategorikal": len(categorical_cols),
        "Missing value": int(missing.sum()),
        "Duplikat": duplicate_count,
    }

    return summary, numerical_cols, categorical_cols, missing


def show_distribution(df: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].hist(df['salary'], bins=30, color='#4C72B0', edgecolor='black', alpha=0.85)
    axes[0].axvline(df['salary'].mean(), color='red', linestyle='--', linewidth=2, label='Rata-rata')
    axes[0].axvline(df['salary'].median(), color='green', linestyle='--', linewidth=2, label='Median')
    axes[0].set_title('Distribusi Salary')
    axes[0].set_xlabel('Salary')
    axes[0].set_ylabel('Frekuensi')
    axes[0].legend()

    avg_salary_exp = df.groupby('experience_years')['salary'].mean().reset_index()
    axes[1].plot(avg_salary_exp['experience_years'], avg_salary_exp['salary'], marker='o', linewidth=2)
    axes[1].set_title('Rata-rata Salary per Experience Years')
    axes[1].set_xlabel('Experience Years')
    axes[1].set_ylabel('Rata-rata Salary')
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def show_correlation(df: pd.DataFrame):
    numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    correlation = df[numerical_cols].corr().round(3)

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(correlation, annot=True, fmt='.3f', cmap='viridis', ax=ax)
    ax.set_title('Heatmap Korelasi Variabel Numerik')
    plt.tight_layout()
    return fig


def show_outlier_summary(df: pd.DataFrame):
    numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    rows = []

    for col in numerical_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outlier_count = int(((df[col] < lower) | (df[col] > upper)).sum())
        outlier_pct = round((outlier_count / len(df)) * 100, 2)
        rows.append([col, round(q1, 2), round(q3, 2), round(iqr, 2), round(lower, 2), round(upper, 2), outlier_count, outlier_pct])

    return pd.DataFrame(rows, columns=['Kolom', 'Q1', 'Q3', 'IQR', 'Batas Bawah', 'Batas Atas', 'Jumlah Outlier', 'Persentase Outlier (%)'])


def main():
    st.set_page_config(page_title='Job Salary Prediction Dashboard', layout='wide')
    st.title('📊 Job Salary Prediction Dashboard')
    st.caption('Versi bersih dari notebook Colab yang siap dijalankan di Streamlit.')

    st.sidebar.header('Pilihan Dataset')
    uploaded_file = st.sidebar.file_uploader('Unggah file CSV lokal (opsional)', type=['csv'])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.sidebar.success('Dataset lokal berhasil dimuat.')
    else:
        try:
            csv_path = get_dataset_path()
            df = pd.read_csv(csv_path)
            st.sidebar.success('Dataset dari Kaggle berhasil dimuat.')
        except Exception as exc:
            st.error(f'Gagal memuat dataset otomatis: {exc}')
            st.info('Silakan unggah file CSV lokal melalui panel samping untuk lanjut.')
            return

    summary, numerical_cols, categorical_cols, missing = summarize_dataframe(df)

    st.subheader('Ringkasan Dataset')
    c1, c2, c3, c4 = st.columns(4)
    c1.metric('Jumlah Baris', f"{summary['Jumlah baris']:,}")
    c2.metric('Jumlah Kolom', summary['Jumlah kolom'])
    c3.metric('Missing Value', summary['Missing value'])
    c4.metric('Duplikat', summary['Duplikat'])

    st.write('')
    col_left, col_right = st.columns(2)
    with col_left:
        st.write('**Kolom numerik:**', ', '.join(numerical_cols) if numerical_cols else 'Tidak ada')
        st.write('**Kolom kategorikal:**', ', '.join(categorical_cols) if categorical_cols else 'Tidak ada')
    with col_right:
        st.dataframe(df.head(10), use_container_width=True)

    st.subheader('Deteksi Data')
    tab1, tab2, tab3, tab4 = st.tabs(['Preview', 'Missing Value', 'Statistik Deskriptif', 'Outlier'])

    with tab1:
        st.dataframe(df.head(20), use_container_width=True)

    with tab2:
        missing_df = pd.DataFrame({
            'Nama Kolom': missing.index,
            'Jumlah Missing Value': missing.values,
            'Persentase Missing Value (%)': (missing.values / len(df) * 100).round(2),
        })
        st.dataframe(missing_df, use_container_width=True)

    with tab3:
        st.dataframe(df[numerical_cols].describe().T.round(2), use_container_width=True)
        if categorical_cols:
            st.dataframe(df[categorical_cols].describe(include='all').T, use_container_width=True)

    with tab4:
        outlier_df = show_outlier_summary(df)
        st.dataframe(outlier_df, use_container_width=True)

    st.subheader('Visualisasi Utama')
    st.pyplot(show_distribution(df), use_container_width=True)

    avg_salary_job = df.groupby('job_title')['salary'].mean().sort_values(ascending=False).reset_index()
    avg_salary_job.columns = ['Job Title', 'Rata-Rata Salary']

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    sns.barplot(data=avg_salary_job.head(10), x='Rata-Rata Salary', y='Job Title', palette='viridis', ax=axes[0])
    axes[0].set_title('10 Jabatan dengan Salary Tertinggi')
    axes[0].set_xlabel('Rata-Rata Salary')
    axes[0].set_ylabel('Job Title')

    avg_salary_edu = df.groupby('education_level')['salary'].mean().sort_values(ascending=False).reset_index()
    sns.barplot(data=avg_salary_edu, x='education_level', y='salary', palette='magma', ax=axes[1])
    axes[1].set_title('Rata-rata Salary Berdasarkan Education Level')
    axes[1].set_xlabel('Education Level')
    axes[1].set_ylabel('Rata-rata Salary')
    axes[1].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)

    st.subheader('Korelasi')
    st.pyplot(show_correlation(df), use_container_width=True)

    st.caption('Aplikasi ini dibuat untuk memudahkan deployment di Streamlit Cloud dan upload ke GitHub.')


if __name__ == '__main__':
    main()
