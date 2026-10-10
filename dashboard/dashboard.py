import os
import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    # Coba cek beberapa kemungkinan lokasi file secara otomatis
    possible_paths = [
        "main_data.csv", 
        "../main_data.csv", 
        "dashboard/main_data.csv"
    ]
    
    file_path = None
    for p in possible_paths:
        if os.path.exists(p):
            file_path = p
            break
            
    if file_path is None:
        st.error("File CSV tidak ditemukan! Pastikan file sudah di-upload ke repository GitHub.")
        return None
        
    df = pd.read_csv(file_path)
    return df
