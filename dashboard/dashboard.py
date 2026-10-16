import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# Set layout halaman Streamlit agar lebih luas
st.set_page_config(page_title="Dashboard Analisis Olist E-Commerce", layout="wide")

# Set style seaborn
sns.set(style="dark")

# Load data utama menggunakan file .gz yang aman dari error ukuran file
base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, "main_data.csv.gz")
all_df = pd.read_csv(csv_path)

# Konversi tanggal
all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'])

# ==========================================
# SIDEBAR: FILTER INTERAKTIF
# ==========================================
st.sidebar.header("🔍 Filter Dashboard")

# 1. Filter Rentang Tahun (Menjawab kebutuhan interaktif reviewer)
all_df['year'] = all_df['order_purchase_timestamp'].dt.year
available_years = sorted(all_df['year'].dropna().unique())
selected_year = st.sidebar.selectbox("Pilih Tahun Transaksi:", options=available_years, index=len(available_years)-1)

# Terapkan filter tahun ke dataframe utama
filtered_df = all_df[all_df['year'] == selected_year]

# ==========================================
# JUDUL UTAMA DASHBOARD
# ==========================================
st.title("Proyek Analisis Data: Olist E-Commerce 🛒")
st.markdown(f"Menampilkan data analisis untuk tahun: **{selected_year}**")
st.markdown("---")

# ==========================================
# VISUALISASI PERTANYAAN 1: Kategori Produk Pendapatan Tertinggi & Terendah
# ==========================================
st.subheader(f"🏆 Performa Kategori Produk (Pendapatan Tertinggi & Terendah) - {selected_year}")

# Kelompokkan data berdasarkan kategori produk
category_revenue = filtered_df.groupby('product_category_name')['payment_value'].sum().reset_index()
category_revenue = category_revenue.sort_values(by='payment_value', ascending=False)

# Ambil 5 teratas dan 5 terbawah
if len(category_revenue) >= 10:
    top_bottom_categories = pd.concat([
        category_revenue.head(5),
        category_revenue.tail(5)
    ]).drop_duplicates()
else:
    top_bottom_categories = category_revenue

fig_cat, ax_cat = plt.subplots(figsize=(12, 6))
sns.barplot(
    x='payment_value', 
    y='product_category_name', 
    data=top_bottom_categories, 
    palette='Blues_r', 
    ax=ax_cat,
    hue='product_category_name',
    legend=False
)
ax_cat.set_title(f"Kategori Produk dengan Total Pendapatan Tertinggi & Terendah ({selected_year})", fontsize=14, fontweight='bold')
ax_cat.set_xlabel("Total Pendapatan (Payment Value)", fontsize=11)
ax_cat.set_ylabel("Kategori Produk", fontsize=11)
st.pyplot(fig_cat)

st.markdown("---")

# ==========================================
# VISUALISASI PERTANYAAN 2: SEGMENTASI RFM & KONTRIBUSI PENDAPATAN
# ==========================================
st.subheader("👥 Analisis Segmentasi Pelanggan (RFM) & Kontribusi Pendapatan")

recent_date = all_df['order_purchase_timestamp'].max()

# Hitung RFM (berdasarkan keseluruhan data agar segmentasi pelanggan akurat)
rfm_df = all_df.groupby('customer_id').agg({
    'order_purchase_timestamp': lambda x: (recent_date - x.max()).days,
    'order_id': 'nunique',
    'payment_value': 'sum'
}).reset_index()

rfm_df.columns = ['customer_id', 'recency', 'frequency', 'monetary']

# Skor RFM
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

# Gabungkan dengan data yang sudah difilter berdasarkan tahun pilihan di sidebar
trans_segment_filtered = pd.merge(filtered_df, rfm_df[['customer_id', 'segment']], on='customer_id', how='inner')

total_revenue_filtered = trans_segment_filtered['payment_value'].sum()
revenue_by_segment = trans_segment_filtered.groupby('segment')['payment_value'].sum().reset_index()

if total_revenue_filtered > 0:
    revenue_by_segment['percentage'] = (revenue_by_segment['payment_value'] / total_revenue_filtered) * 100
else:
    revenue_by_segment['percentage'] = 0

# Menampilkan grafik menggunakan 2 kolom di Streamlit
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
        palette='Blues_r',
        hue='segment',
        legend=False
    )
    ax.set_title(f"Jumlah Transaksi Pelanggan per Segmen ({selected_year})", fontsize=11, fontweight='bold')
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
        palette='Greens_r',
        hue='segment',
        legend=False
    )
    ax.set_title(f"Kontribusi Pendapatan ({selected_year}) per Segmen (%)", fontsize=11, fontweight='bold')
    ax.set_xlabel("Segmen Pelanggan", fontsize=10)
    ax.set_ylabel("Persentase Pendapatan (%)", fontsize=10)
    plt.xticks(rotation=15)
    st.pyplot(fig)
