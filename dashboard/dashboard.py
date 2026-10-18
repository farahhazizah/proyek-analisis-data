import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# Set layout halaman Streamlit agar lebih luas
st.set_page_config(page_title="Dashboard Analisis Olist E-Commerce", layout="wide")

# Set style seaborn
sns.set(style="darkgrid")

# Load data utama
base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, "main_data.csv")
all_df = pd.read_csv(csv_path)

# Konversi kolom tanggal ke datetime
all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'])

# ==========================================
# SIDEBAR: FILTER INTERAKTIF
# ==========================================
st.sidebar.header("🔍 Filter Dashboard")

min_date = all_df['order_purchase_timestamp'].min().date()
max_date = all_df['order_purchase_timestamp'].max().date()

try:
    start_date, end_date = st.sidebar.date_input(
        label='Rentang Waktu',
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
except Exception:
    start_date, end_date = min_date, max_date

filtered_df = all_df[
    (all_df['order_purchase_timestamp'].dt.date >= start_date) & 
    (all_df['order_purchase_timestamp'].dt.date <= end_date)
]

# ==========================================
# JUDUL UTAMA DASHBOARD
# ==========================================
st.title("Proyek Analisis Data: Olist E-Commerce 🛒")
st.markdown(f"Menampilkan data dari tanggal: **{start_date}** sampai **{end_date}**")
st.markdown("---")

# ==========================================
# VISUALISASI PERTANYAAN 1: Produk Pendapatan Tertinggi & Terendah
# ==========================================
st.subheader("🏆 Performa Produk berdasarkan Pendapatan (Top & Bottom)")

if 'product_id' in filtered_df.columns and 'payment_value' in filtered_df.columns:
    product_revenue = filtered_df.groupby('product_id')['payment_value'].sum().reset_index()
    product_revenue = product_revenue.sort_values(by='payment_value', ascending=False)

    top_products = product_revenue.head(5)
    bottom_products = product_revenue.tail(5)
    top_bottom_products = pd.concat([top_products, bottom_products]).drop_duplicates()

    top_bottom_products['short_product_id'] = top_bottom_products['product_id'].str[:8] + "..."

    fig_cat, ax_cat = plt.subplots(figsize=(12, 5))
    sns.barplot(
        x='payment_value', 
        y='short_product_id', 
        data=top_bottom_products, 
        color='#1f77b4', 
        ax=ax_cat
    )
    ax_cat.set_title("Produk dengan Total Pendapatan Tertinggi & Terendah", fontsize=12, fontweight='bold')
    ax_cat.set_xlabel("Total Pendapatan (Payment Value)", fontsize=10)
    ax_cat.set_ylabel("ID Produk", fontsize=10)
    st.pyplot(fig_cat)

st.markdown("---")

# ==========================================
# VISUALISASI PERTANYAAN 2: SEGMENTASI RFM & KONTRIBUSI PENDAPATAN
# ==========================================
st.subheader("👥 Analisis Segmentasi Pelanggan (RFM) & Kontribusi Pendapatan")

recent_date = all_df['order_purchase_timestamp'].max()

# Menggunakan customer_unique_id agar agregasi RFM akurat
rfm_df = all_df.groupby('customer_unique_id').agg({
    'order_purchase_timestamp': lambda x: (recent_date - x.max()).days,
    'order_id': 'nunique',
    'payment_value': 'sum'
}).reset_index()

rfm_df.columns = ['customer_unique_id', 'recency', 'frequency', 'monetary']

rfm_df['r_score'] = pd.qcut(rfm_df['recency'], 5, labels=[5, 4, 3, 2, 1], duplicates='drop')
rfm_df['f_score'] = pd.qcut(rfm_df['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
rfm_df['m_score'] = pd.qcut(rfm_df['monetary'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])

def customer_segment(row):
    if row['r_score'] >= 4 and row['f_score'] >= 4 and row['m_score'] >= 4:
        return 'Best Customers'
    elif row['f_score'] >= 3:
        return 'Loyal Customers'
    elif row['r_score'] <= 2:
        return 'At Risk Customers'
    else:
        return 'Potential Loyalist'

rfm_df['segment'] = rfm_df.apply(customer_segment, axis=1)

trans_segment_filtered = pd.merge(filtered_df, rfm_df[['customer_unique_id', 'segment']], on='customer_unique_id', how='inner')

total_revenue_filtered = trans_segment_filtered['payment_value'].sum()
revenue_by_segment = trans_segment_filtered.groupby('segment')['payment_value'].sum().reset_index()

if total_revenue_filtered > 0:
    revenue_by_segment['percentage'] = (revenue_by_segment['payment_value'] / total_revenue_filtered) * 100
else:
    revenue_by_segment['percentage'] = 0

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(8, 5))
    seg_counts = trans_segment_filtered['segment'].value_counts().reset_index()
    seg_counts.columns = ['segment', 'count']
    sns.barplot(
        x='segment', 
        y='count', 
        data=seg_counts, 
        ax=ax, 
        color='#2ca02c'
    )
    ax.set_title("Jumlah Transaksi Pelanggan per Segmen", fontsize=11, fontweight='bold')
    ax.set_xlabel("Segmen Pelanggan", fontsize=10)
    ax.set_ylabel("Jumlah", fontsize=10)
    plt.xticks(rotation=15)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        x='segment', 
        y='percentage', 
        data=revenue_by_segment, 
        ax=ax, 
        color='#ff7f0e'
    )
    ax.set_title("Kontribusi Pendapatan per Segmen (%)", fontsize=11, fontweight='bold')
    ax.set_xlabel("Segmen Pelanggan", fontsize=10)
    ax.set_ylabel("Persentase Pendapatan (%)", fontsize=10)
    plt.xticks(rotation=15)
    st.pyplot(fig)
