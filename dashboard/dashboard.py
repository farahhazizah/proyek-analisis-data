import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

# Set layout halaman Streamlit agar lebih luas
st.set_page_config(page_title="Dashboard Analisis Olist E-Commerce", layout="wide")

# Set style seaborn
sns.set(style="darkgrid")


# Load data utama dengan caching agar performa cepat
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "main_data.csv")  
    
    df = pd.read_csv(csv_path)
    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"]
    )
    return df

all_df = load_data()

# ==========================================
# SIDEBAR: FILTER INTERAKTIF
# ==========================================
st.sidebar.header("🔍 Filter Dashboard")

min_date = all_df["order_purchase_timestamp"].min().date()
max_date = all_df["order_purchase_timestamp"].max().date()

try:
    start_date, end_date = st.sidebar.date_input(
        label="Rentang Waktu",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date,
    )
except Exception:
    start_date, end_date = min_date, max_date

# Validasi rentang tanggal
if isinstance(start_date, (list, tuple)) and len(start_date) == 2:
    start_date, end_date = start_date

filtered_df = all_df[
    (all_df["order_purchase_timestamp"].dt.date >= start_date)
    & (all_df["order_purchase_timestamp"].dt.date <= end_date)
]

# ==========================================
# JUDUL UTAMA DASHBOARD
# ==========================================
st.title("Proyek Analisis Data: Olist E-Commerce 🛒")
st.markdown(
    f"Menampilkan data dari tanggal: **{start_date}** sampai **{end_date}**"
)
st.markdown("---")

# Cek jika data hasil filter kosong
if filtered_df.empty:
    st.warning(
        "⚠️ Tidak ada data untuk rentang tanggal yang dipilih. Silakan sesuaikan kembali filter tanggal."
    )
else:
    # ==========================================
    # VISUALISASI PERTANYAAN 1: Performa Kategori Produk (Top & Bottom 5)
    # ==========================================
    st.subheader("🏆 Performa Penjualan Berdasarkan Kategori Produk")

    if "product_category_name" in filtered_df.columns and "price" in filtered_df.columns:
        category_perf = (
            filtered_df.groupby("product_category_name")
            .agg({"price": "sum", "order_id": "nunique"})
            .reset_index()
        )
        category_perf.columns = ["product_category_name", "total_revenue", "total_orders"]
        
        top_5 = category_perf.sort_values(by="total_revenue", ascending=False).head(5)
        bottom_5 = category_perf.sort_values(by="total_revenue", ascending=True).head(5)

        # Buat visualisasi subplot (Top & Bottom 5 berdampingan seperti di notebook)
        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(18, 6))

        # Grafik Top 5 Kategori
        sns.barplot(
            x="total_revenue",
            y="product_category_name",
            data=top_5,
            palette="Blues_r",
            ax=ax[0],
            hue="product_category_name",
            legend=False,
        )
        ax[0].set_ylabel(None)
        ax[0].set_xlabel("Total Revenue (R$)", fontsize=12)
        ax[0].set_title("Top 5 Best Performing Product Categories", fontsize=14, fontweight="bold")

        # Grafik Bottom 5 Kategori
        sns.barplot(
            x="total_revenue",
            y="product_category_name",
            data=bottom_5,
            palette="Blues_r",
            ax=ax[1],
            hue="product_category_name",
            legend=False,
        )
        ax[1].set_ylabel(None)
        ax[1].set_xlabel("Total Revenue (R$)", fontsize=12)
        ax[1].set_title("Bottom 5 Worst Performing Product Categories", fontsize=14, fontweight="bold")
        ax[1].yaxis.set_label_position("right")
        ax[1].yaxis.tick_right()

        plt.suptitle("Performa Penjualan Berdasarkan Kategori Produk", fontsize=16, fontweight="bold", y=1.05)
        st.pyplot(fig)

    st.markdown("---")

    # ==========================================
    # VISUALISASI PERTANYAAN 2: SEGMENTASI RFM & KONTRIBUSI PENDAPATAN
    # ==========================================
    st.subheader("👥 Analisis Segmentasi Pelanggan (RFM) & Kontribusi Pendapatan")

    recent_date = all_df["order_purchase_timestamp"].max()

    rfm_df = (
        all_df.groupby("customer_unique_id")
        .agg({
            "order_purchase_timestamp": lambda x: (recent_date - x.max()).days,
            "order_id": "nunique",
            "payment_value": "sum",
        })
        .reset_index()
    )

    rfm_df.columns = ["customer_unique_id", "recency", "frequency", "monetary"]

    rfm_df["r_score"] = pd.qcut(
        rfm_df["recency"].rank(method="first"), 5, labels=[5, 4, 3, 2, 1]
    )
    rfm_df["f_score"] = pd.qcut(
        rfm_df["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]
    )
    rfm_df["m_score"] = pd.qcut(
        rfm_df["monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]
    )

    rfm_df["r_score"] = rfm_df["r_score"].astype(int)
    rfm_df["f_score"] = rfm_df["f_score"].astype(int)
    rfm_df["m_score"] = rfm_df["m_score"].astype(int)

    def customer_segment(row):
        if row["r_score"] >= 4 and row["f_score"] >= 4 and row["m_score"] >= 4:
            return "Best Customers"
        elif row["f_score"] >= 3:
            return "Loyal Customers"
        elif row["r_score"] <= 2:
            return "At Risk Customers"
        else:
            return "Potential Loyalist"

    rfm_df["segment"] = rfm_df.apply(customer_segment, axis=1)

    trans_segment_filtered = pd.merge(
        filtered_df,
        rfm_df[["customer_unique_id", "segment"]],
        on="customer_unique_id",
        how="inner",
    )

    total_revenue_filtered = trans_segment_filtered["payment_value"].sum()
    revenue_by_segment = (
        trans_segment_filtered.groupby("segment")["payment_value"]
        .sum()
        .reset_index()
    )

    if total_revenue_filtered > 0:
        revenue_by_segment["percentage"] = (
            revenue_by_segment["payment_value"] / total_revenue_filtered
        ) * 100
    else:
        revenue_by_segment["percentage"] = 0

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(8, 5))
        seg_counts = (
            trans_segment_filtered["segment"].value_counts().reset_index()
        )
        seg_counts.columns = ["segment", "count"]
        sns.barplot(
            x="segment", y="count", data=seg_counts, ax=ax, color="#2ca02c"
        )
        ax.set_title(
            "Jumlah Transaksi Pelanggan per Segmen",
            fontsize=11,
            fontweight="bold",
        )
        ax.set_xlabel("Segmen Pelanggan", fontsize=10)
        ax.set_ylabel("Jumlah", fontsize=10)
        ax.tick_params(axis="x", rotation=15)
        st.pyplot(fig)

    with col2:
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(
            x="segment",
            y="percentage",
            data=revenue_by_segment,
            ax=ax,
            color="#ff7f0e",
        )
        ax.set_title(
            "Kontribusi Pendapatan per Segmen (%)",
            fontsize=11,
            fontweight="bold",
        )
        ax.set_xlabel("Segmen Pelanggan", fontsize=10)
        ax.set_ylabel("Persentase Pendapatan (%)", fontsize=10)
        ax.tick_params(axis="x", rotation=15)
        st.pyplot(fig)
