import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set page config
st.set_page_config(
    page_title="Olist E-Commerce Dashboard",
    page_icon="📊",
    layout="wide"
)

# Load data function dengan pencarian path otomatis
@st.cache_data
def load_data():
    possible_paths = [
        "main_data.csv.gz",
        "../main_data.csv.gz",
        "dashboard/main_data.csv.gz",
        "main_data.csv",
        "../main_data.csv"
    ]
    
    file_path = None
    for p in possible_paths:
        if os.path.exists(p):
            file_path = p
            break
            
    if file_path is None:
        st.error("File dataset (main_data.csv.gz) tidak ditemukan! Pastikan file sudah di-upload ke repository GitHub.")
        return None
        
    df = pd.read_csv(file_path)
    
    # Konversi kolom tanggal jika ada
    if 'order_purchase_timestamp' in df.columns:
        df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
        
    return df

df = load_data()

if df is not None and not df.empty:
    # Sidebar / Filter Tanggal
    st.sidebar.header("Filter Dashboard")
    
    if 'order_purchase_timestamp' in df.columns:
        min_date = df['order_purchase_timestamp'].min().date()
        max_date = df['order_purchase_timestamp'].max().date()
        
        start_date, end_date = st.sidebar.date_input(
            "Rentang Tanggal",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
        
        # Filter dataframe berdasarkan tanggal
        filtered_df = df[(df['order_purchase_timestamp'].dt.date >= start_date) & 
                         (df['order_purchase_timestamp'].dt.date <= end_date)]
    else:
        filtered_df = df

    # Judul Utama Dashboard
    st.title("📊 Olist E-Commerce Data Analysis Dashboard")
    st.markdown("Dashboard interaktif untuk menganalisis performa penjualan, tren pesanan, dan status pengiriman.")

    # Bagian Metrik Utama (Top Metrics)
    col1, col2, col3 = st.columns(3)
    
    total_orders = filtered_df['order_id'].nunique() if 'order_id' in filtered_df.columns else len(filtered_df)
    total_revenue = filtered_df['price'].sum() if 'price' in filtered_df.columns else 0
    total_customers = filtered_df['customer_id'].nunique() if 'customer_id' in filtered_df.columns else 0
    
    with col1:
        st.metric("Total Pesanan", f"{total_orders:,}")
    with col2:
        st.metric("Total Pendapatan", f"$ {total_revenue:,.2f}")
    with col3:
        st.metric("Total Pelanggan", f"{total_customers:,}")

    st.divider()

    # Grafik 1: Tren Pesanan Bulanan
    st.subheader("📈 Tren Jumlah Pesanan Bulanan")
    if 'order_purchase_timestamp' in filtered_df.columns:
        monthly_orders = filtered_df.resample('ME', on='order_purchase_timestamp').agg({'order_id': 'nunique'}).reset_index()
        monthly_orders['month_year'] = monthly_orders['order_purchase_timestamp'].dt.strftime('%Y-%m')
        
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(monthly_orders['month_year'], monthly_orders['order_id'], marker='o', color='#1f77b4', linewidth=2)
        plt.xticks(rotation=45)
        ax.set_xlabel("Bulan")
        ax.set_ylabel("Jumlah Pesanan")
        ax.grid(True, linestyle='--', alpha=0.6)
        st.pyplot(fig)
    else:
        st.info("Kolom tanggal pesanan tidak ditemukan pada dataset.")

    # Grafik 2: Distribusi Status Pesanan
    st.subheader("📦 Distribusi Status Pesanan")
    if 'order_status' in filtered_df.columns:
        status_counts = filtered_df['order_status'].value_counts().reset_index()
        status_counts.columns = ['order_status', 'count']
        
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(data=status_counts, x='count', y='order_status', palette='viridis', ax=ax)
        ax.set_xlabel("Jumlah")
        ax.set_ylabel("Status Pesanan")
        st.pyplot(fig)
    else:
        st.info("Kolom status pesanan tidak ditemukan pada dataset.")

else:
    st.warning("Data belum dimuat dengan benar. Periksa kembali file dataset Anda di GitHub.")
