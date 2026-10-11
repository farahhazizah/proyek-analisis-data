import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Konfigurasi Halaman Dashboard
st.set_page_config(page_title="Olist E-Commerce Dashboard", page_icon="📊", layout="wide")

# Title & Header
st.title("📊 Proyek Analisis Data: Olist E-Commerce")
st.markdown("---")

# Load Dataset
@st.cache_data
def load_data():
    if os.path.exists("main_data.csv"):
        return pd.read_csv("main_data.csv")
    elif os.path.exists("dashboard/main_data.csv"):
        return pd.read_csv("dashboard/main_data.csv")
    else:
        return pd.read_csv("../dashboard/main_data.csv")

df = load_data()

# Sidebar
st.sidebar.header("🔍 Informasi Proyek")
st.sidebar.markdown("**Nama:** Farah Azizah")
st.sidebar.markdown("**Dataset:** Olist E-Commerce")

# Filter Sederhana di Sidebar
categories = df['product_category_name'].dropna().unique().tolist()
selected_categories = st.sidebar.multiselect(
    "Filter Kategori Produk:",
    options=categories,
    default=categories[:10] if len(categories) >= 10 else categories
)

filtered_df = df[df['product_category_name'].isin(selected_categories)] if selected_categories else df

# Section 1: Performa Kategori Produk (Top & Bottom)
st.subheader("🏆 Performa Kategori Produk Berdasarkan Pendapatan")

category_perf = filtered_df.groupby('product_category_name').agg({
    'price': 'sum',
    'order_id': 'count'
}).reset_index()
category_perf.columns = ['product_category_name', 'total_revenue', 'total_orders']

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### Top 5 Kategori (Pendapatan Tertinggi)")
    top_5 = category_perf.sort_values(by='total_revenue', ascending=False).head(5)
    
    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = ["#1f77b4" if i == 0 else "#d3d3d3" for i in range(len(top_5))]
    sns.barplot(x='total_revenue', y='product_category_name', data=top_5, palette=colors, ax=ax)
    ax.set_xlabel("Total Revenue (R$)")
    ax.set_ylabel(None)
    st.pyplot(fig)

with col2:
    st.markdown("##### Bottom 5 Kategori (Pendapatan Terendah)")
    bottom_5 = category_perf.sort_values(by='total_revenue', ascending=True).head(5)
    
    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = ["#d62728" if i == 0 else "#d3d3d3" for i in range(len(bottom_5))]
    sns.barplot(x='total_revenue', y='product_category_name', data=bottom_5, palette=colors, ax=ax)
    ax.set_xlabel("Total Revenue (R$)")
    ax.set_ylabel(None)
    st.pyplot(fig)

st.markdown("---")
st.caption("© 2026 - Olist E-Commerce Dashboard | Farah Azizah")
