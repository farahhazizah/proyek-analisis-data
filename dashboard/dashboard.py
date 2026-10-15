import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# Set style seaborn
sns.set(style="dark")

# Load data utama menggunakan file .gz yang aman dari error ukuran file
base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, "main_data.csv.gz")
all_df = pd.read_csv(csv_path)

st.title("Proyek Analisis Data: Olist E-Commerce 🛒")

# --- VISUALISASI PERTANYAAN 2: SEGMENTASI RFM & KONTRIBUSI PENDAPATAN ---
st.subheader("Analisis Segmentasi Pelanggan (RFM) & Kontribusi Pendapatan")

# Konversi tanggal
all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'])
recent_date = all_df['order_purchase_timestamp'].max()

# Hitung RFM
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

# Kontribusi Pendapatan 2018
df_2018 = all_df[all_df['order_purchase_timestamp'].dt.year == 2018]
trans_segment_2018 = pd.merge(df_2018, rfm_df[['customer_id', 'segment']], on='customer_id', how='inner')

total_revenue_2018 = trans_segment_2018['payment_value'].sum()
revenue_by_segment_2018 = trans_segment_2018.groupby('segment')['payment_value'].sum().reset_index()
revenue_by_segment_2018['percentage'] = (revenue_by_segment_2018['payment_value'] / total_revenue_2018) * 100

# Menampilkan grafik menggunakan 2 kolom di Streamlit
col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(8, 5))
    seg_counts = rfm_df['segment'].value_counts().reset_index()
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
    ax.set_title("Jumlah Pelanggan per Segmen", fontsize=12, fontweight='bold')
    ax.set_xlabel("Segmen Pelanggan", fontsize=10)
    ax.set_ylabel("Jumlah Pelanggan", fontsize=10)
    plt.xticks(rotation=15)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        x='segment', 
        y='percentage', 
        data=revenue_by_segment_2018, 
        ax=ax, 
        palette='Greens_r',
        hue='segment',
        legend=False
    )
    ax.set_title("Kontribusi Pendapatan (2018) per Segmen (%)", fontsize=12, fontweight='bold')
    ax.set_xlabel("Segmen Pelanggan", fontsize=10)
    ax.set_ylabel("Persentase Pendapatan (%)", fontsize=10)
    plt.xticks(rotation=15)
    st.pyplot(fig)
