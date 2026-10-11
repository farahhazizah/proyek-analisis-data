import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Konfigurasi Halaman Dashboard
st.set_page_config(page_title="Olist E-Commerce Dashboard", page_icon="📊", layout="wide")

st.title("📊 Proyek Analisis Data: Olist E-Commerce")
st.markdown("---")

# Memuat Dataset Bersih dengan aman
@st.cache_data
def load_data():
    # Mendeteksi path file main_data.csv agar tidak error FileNotFoundError
    if os.path.exists("main_data.csv"):
        return pd.read_csv("main_data.csv")
    elif os.path.exists("dashboard/main_data.csv"):
        return pd.read_csv("dashboard/main_data.csv")
    else:
        return pd.read_csv("../dashboard/main_data.csv")

df = load_data()

# Sidebar / Navigasi Sederhana
st.sidebar.header("🔍 Informasi Proyek")
st.sidebar.markdown("**Nama:** Farah Azizah")
st.sidebar.markdown("**Proyek:** Analisis Data E-Commerce Olist")

# Pertanyaan Bisnis 1: Performa Kategori Produk
st.subheader("🏆 Performa Kategori Produk Berdasarkan Pendapatan")

category_perf = df.groupby('product_category_name').agg({
    'price': 'sum',
    'order_id': 'count'
}).reset_index()
category_perf.columns = ['product_category_name', 'total_revenue', 'total_orders']

top_5_cat = category_perf.sort_values(by='total_revenue', ascending=False).head(5)

fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(
    x='total_revenue', 
    y='product_category_name', 
    data=top_5_cat, 
    palette='Blues_r', 
    ax=ax
)
ax.set_title("Top 5 Kategori Pendapatan Tertinggi")
ax.set_xlabel("Total Revenue (R$)")
ax.set_ylabel("Kategori Produk")
st.pyplot(fig)

st.markdown("---")
st.caption("© 2026 - Olist E-Commerce Dashboard")