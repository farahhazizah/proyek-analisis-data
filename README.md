# Proyek Analisis Data: Olist E-Commerce Dataset 📊

Proyek ini merupakan submission akhir untuk kelas Belajar Analisis Data dengan Python di Dicoding. Proyek ini bertujuan untuk melakukan analisis eksplorasi data (EDA) pada dataset e-commerce Olist guna memperoleh insight bisnis terkait performa produk, kepuasan pelanggan, serta segmentasi pelanggan.

## Setup Environment - Anaconda
```bash
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt

## Setup Environment - Shell/Terminal 
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt

## Run Streamlit App
streamlit run dashboard/dashboard.py
