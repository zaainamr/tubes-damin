# Job Salary Prediction Dashboard 📊

Aplikasi data mining komprehensif untuk analisis dan prediksi gaji karyawan menggunakan machine learning. Dashboard ini mengintegrasikan teknik clustering, regression, dan classification untuk memberikan insights mendalam tentang kompensasi karyawan.

## Fitur Utama

### 1. **Data Understanding** 📈
- Preview dataset dengan lebih dari 250,000 data karyawan
- Analisis deskriptif variabel numerik dan kategorikal
- Deteksi missing value, data duplikat, dan outlier
- Visualisasi distribusi gaji dan korelasi variabel

### 2. **Data Preparation** 🔧
- **Ordinal Encoding**: Untuk variabel kategorikal berhierarkis (Education Level, Company Size)
- **One-Hot Encoding**: Untuk variabel kategorikal nominal (Job Title, Industry, Location, Remote Work)
- **Feature Scaling**: StandardScaler untuk normalisasi data numerik

### 3. **Data Modeling** 🤖

#### K-Means Clustering
- Segmentasi otomatis karyawan ke dalam kelompok dengan karakteristik serupa
- Penentuan jumlah cluster optimal menggunakan Elbow Method dan Silhouette Score
- Visualisasi cluster menggunakan PCA (2D projection)

#### Linear Regression
- Prediksi nilai gaji (variabel kontinu)
- Evaluasi model menggunakan R², RMSE, dan MAE
- Cross-validation (5-Fold) untuk validasi generalisasi model

#### Random Forest Classification
- Klasifikasi karyawan berdasarkan kelompok pendapatan
- Evaluasi menggunakan Accuracy, Precision, Recall, F1-Score
- Confusion Matrix dan Classification Report

## Dataset

**Source**: Kaggle - Job Salary Prediction Dataset  
**URL**: https://www.kaggle.com/datasets/nalisha/job-salary-prediction-dataset

## Instalasi & Setup

### Prerequisites
- Python 3.8+
- pip

### Step 1: Clone Repository
```bash
git clone https://github.com/username/tubes-damin.git
cd tubes-damin
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Jalankan Aplikasi
```bash
streamlit run app_streamlit.py
```

Aplikasi akan membuka di browser di `http://localhost:8501`

## Deploy ke Streamlit Cloud

1. Push repository ke GitHub
2. Buka https://share.streamlit.io
3. Pilih repository dan file `app_streamlit.py`
4. Deploy aplikasi

## Struktur Project

```
tubes-damin/
├── app_streamlit.py          # Main Streamlit application
├── requirements.txt           # Python dependencies
├── README.md                  # Documentation (ini)
└── Tubes_Datmin.ipynb         # Original Jupyter notebook (reference)
```

## Dependencies

```
streamlit>=1.38.0
pandas>=2.2.0
numpy>=1.26.0
matplotlib>=3.8.0
seaborn>=0.13.0
kagglehub>=0.3.0
scikit-learn>=1.3.0
```

## Catatan Penting

- Aplikasi ini akan secara otomatis mengunduh dataset dari Kaggle saat pertama kali dijalankan
- Jika koneksi gagal, aplikasi akan menggunakan dummy data untuk demo
- Semua dependencies sudah tersedia di `requirements.txt`

## Author

**Created**: 2024  
**Purpose**: Tugas Besar - Data Mining & Machine Learning  
**Status**: Production Ready ✅
