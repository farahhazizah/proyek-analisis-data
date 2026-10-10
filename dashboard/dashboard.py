import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Olist E-Commerce Dashboard",
    page_icon="📊",
    layout="wide",
)

# Load data
@st.cache_data
def load_data():
    customers_df = pd.read_csv("customers_dataset.csv")
    orders_df = pd.read_csv("orders_dataset.csv")
    order_items_df = pd.read_csv("order_items_dataset.csv")
    order_payments_df = pd.read_csv("order_payments_dataset.csv")
    products_df = pd.read_csv("products_dataset.csv")
    product_category_name_translation = pd.read_csv("product_category_name_translation.csv")

    orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])
    return customers_df, orders_df, order_items_df, order_payments_df, products_df, product_category_name_translation

customers_df, orders_df, order_items_df, order_payments_df, products_df, product_category_name_translation = load_data()

# Sidebar Filter
st.sidebar.header("Filter Berdasarkan Waktu")
min_date = orders_df['order_purchase_timestamp'].min().date()
max_date = orders_df['order_purchase_timestamp'].max().date()

start_date, end_date = st.sidebar.date_input(
    "Rentang Waktu",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

main_df = orders_df[(orders_df['order_purchase_timestamp'].dt.date >= start_date) &
                    (orders_df['order_purchase_timestamp'].dt.date <= end_date)]

# Title
st.title("📊 Olist E-Commerce Dashboard Analisis")
st.markdown("Dashboard interaktif untuk memantau performa kategori produk dan segmentasi pelanggan (*RFM Analysis*).")

# Pertanyaan 1
st.subheader("🏆 Performa Kategori Produk Berdasarkan Pendapatan")
order_items_products = pd.merge(order_items_df, products_df, on="product_id", how="inner")
complete_order_df = pd.merge(order_items_products, product_category_name_translation, on="product_category_name", how="inner")
filtered_order_items = complete_order_df[complete_order_df['order_id'].isin(main_df['order_id'])]

category_revenue = filtered_order_items.groupby(by="product_category_name_english").agg({
    "price": "sum",
    "order_id": "nunique"
}).reset_index()
category_revenue.rename(columns={"price": "total_revenue", "order_id": "total_orders"}, inplace=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("#### Top 5 Kategori Pendapatan Tertinggi")
    top_5 = category_revenue.sort_values(by="total_revenue", ascending=False).head(5)
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(x="total_revenue", y="product_category_name_english", data=top_5, palette=["#72BCD4"] + ["#D3D3D3"]*4, ax=ax)
    ax.set_ylabel(None)
    ax.set_xlabel("Total Revenue (R$)")
    st.pyplot(fig)

with col2:
    st.markdown("#### Bottom 5 Kategori Pendapatan Terendah")
    bottom_5 = category_revenue.sort_values(by="total_revenue", ascending=True).head(5)
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(x="total_revenue", y="product_category_name_english", data=bottom_5, palette=["#72BCD4"] + ["#D3D3D3"]*4, ax=ax)
    ax.set_ylabel(None)
    ax.set_xlabel("Total Revenue (R$)")
    st.pyplot(fig)

# Pertanyaan 2 (RFM)
st.subheader("👥 Analisis Segmentasi Pelanggan (RFM Analysis)")
rfm_df = main_df.merge(order_payments_df, on="order_id", how="inner")
rfm_df = rfm_df.merge(customers_df, on="customer_id", how="inner")
recent_date = main_df['order_purchase_timestamp'].max()

rfm_analysis = rfm_df.groupby(by="customer_unique_id", as_index=False).agg({
    "order_purchase_timestamp": lambda x: (recent_date - x.max()).days,
    "order_id": "nunique",
    "payment_value": "sum"
})
rfm_analysis.columns = ["customer_id", "recency", "frequency", "monetary"]

col3, col4, col5 = st.columns(3)
with col3:
    st.markdown("#### Best by Recency (Days)")
    top_recency = rfm_analysis.sort_values(by="recency", ascending=True).head(5)
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.barplot(y="recency", x="customer_id", data=top_recency, palette=["#72BCD4"] + ["#D3D3D3"]*4, ax=ax)
    ax.set_xticklabels([])
    ax.set_xlabel("Customer ID")
    ax.set_ylabel("Recency (Days)")
    st.pyplot(fig)

with col4:
    st.markdown("#### Best by Frequency")
    top_freq = rfm_analysis.sort_values(by="frequency", ascending=False).head(5)
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.barplot(y="frequency", x="customer_id", data=top_freq, palette=["#72BCD4"] + ["#D3D3D3"]*4, ax=ax)
    ax.set_xticklabels([])
    ax.set_xlabel("Customer ID")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)

with col5:
    st.markdown("#### Best by Monetary")
    top_monetary = rfm_analysis.sort_values(by="monetary", ascending=False).head(5)
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.barplot(y="monetary", x="customer_id", data=top_monetary, palette=["#72BCD4"] + ["#D3D3D3"]*4, ax=ax)
    ax.set_xticklabels([])
    ax.set_xlabel("Customer ID")
    ax.set_ylabel("Monetary (R$)")
    st.pyplot(fig)

st.caption("Copyright (c) 2026 - Proyek Analisis Data Olist")
