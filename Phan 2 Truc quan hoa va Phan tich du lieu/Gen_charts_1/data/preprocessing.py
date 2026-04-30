import pandas as pd
import numpy as np
import os

# =====================================================================
# CẤU HÌNH THÔNG SỐ
# =====================================================================
FILE_INPUT = 'df_master.csv' 
FILE_OUTPUT = 'master_data_final.csv'
SENTINEL_DATE = pd.to_datetime('1900-01-01')

# --- HÀM 1: ĐỌC DATA AN TOÀN ---
def load_data_robustly(file_path):
    if file_path.endswith('.xlsx'):
        try: return pd.read_excel(file_path)
        except: pass
    for enc in ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']:
        try: return pd.read_csv(file_path, encoding=enc)
        except: continue
    raise ValueError("Không thể đọc file. Kiểm tra lại định dạng!")

# --- HÀM 2: LÀM SẠCH (PREPROCESSING) ---
def clean_data(df):
    print("[1/3] Đang làm sạch và chuẩn hóa dữ liệu...")
    # Xử lý ngày tháng & Sentinel Value
    date_cols = ['order_date', 'signup_date', 'ship_date', 'delivery_date']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            df[f'{col}_is_missing'] = df[col].isnull().astype('int8')
            df[col] = df[col].fillna(SENTINEL_DATE)

    # Fill missing các cột khác
    for col in df.columns:
        if col in date_cols or col.endswith('_is_missing'): continue
        if df[col].isnull().any():
            fill_val = 'unknown' if df[col].dtype == 'object' else 0
            df[col] = df[col].fillna(fill_val)
    
    # Chuẩn hóa văn bản
    text_cols = df.select_dtypes(include=['object']).columns
    for col in text_cols:
        df[col] = df[col].astype(str).str.lower().str.strip()
    
    return df

# --- HÀM 3: TẠO CHỈ SỐ KINH DOANH (FEATURE ENGINEERING) ---
def create_features(df):
    print("[2/3] Đang tính toán các chỉ số Revenue, Profit, Lead Time...")
    # Revenue, Cogs, Profit
    df['order_revenue'] = (df['quantity'] * df['unit_price']).astype('float32')
    df['order_cogs'] = (df['quantity'] * df['cogs']).astype('float32')
    df['order_profit'] = df['order_revenue'] - df['order_cogs']
    
    # Lead Time logic
    df['lead_time'] = (df['delivery_date'] - df['order_date']).dt.days
    if 'delivery_date_is_missing' in df.columns:
        df.loc[df['delivery_date_is_missing'] == 1, 'lead_time'] = -1
    df['lead_time'] = df['lead_time'].astype('int32')
    
    return df

# =====================================================================
# HÀM MAIN - NHẠC TRƯỞNG
# =====================================================================
def main():
    print(f"=== KHỞI ĐỘNG PIPELINE DỮ LIỆU DATATHON 2026 ===")
    
    if not os.path.exists(FILE_INPUT):
        print(f"❌ Lỗi: Không tìm thấy file {FILE_INPUT}")
        return

    try:
        # Bước 1: Load
        raw_df = load_data_robustly(FILE_INPUT)
        print(f"✅ Đã tải dữ liệu: {raw_df.shape[0]} dòng.")

        # Bước 2: Clean
        df_cleaned = clean_data(raw_df)

        # Bước 3: Feature Engineering
        df_final = create_features(df_cleaned)

        # Bước 4: Sắp xếp & Lưu
        df_final = df_final.sort_values(by='order_date').reset_index(drop=True)
        df_final.to_csv(FILE_OUTPUT, index=False)
        
        print(f"✅ THÀNH CÔNG! File Master đã lưu tại: {FILE_OUTPUT}")
        print(f"📊 Kích thước Master Data: {df_final.shape}")
        
    except Exception as e:
        print(f"❌ Quá trình thất bại. Lỗi: {e}")

if __name__ == "__main__":
    main()