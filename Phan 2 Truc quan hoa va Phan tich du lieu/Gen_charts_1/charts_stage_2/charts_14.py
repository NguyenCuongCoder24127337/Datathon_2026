import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import matplotlib.ticker as ticker
from matplotlib.lines import Line2D

# =====================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN & THEME (VIBRANT EDITION)
# =====================================================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
PATH_MASTER = os.path.join(BASE_DIR, 'data', 'master_data_final.csv')

# Bảng màu Vibrant
VIBRANT = [
    '#E63946',  # 0  đỏ san hô
    '#2196F3',  # 1  xanh dương cobalt
    '#FF9800',  # 2  cam amber
    '#4CAF50',  # 3  xanh lá emerald
    '#9C27B0',  # 4  tím violet
    '#00BCD4',  # 5  cyan teal
    '#FF5722',  # 6  đỏ cam deep-orange
    '#3F51B5',  # 7  indigo
    '#FFEB3B',  # 8  vàng canary
    '#009688',  # 9  teal đậm
]

BG_COLOR      = '#FAFAFA'
GRID_COLOR    = '#E0E0E0'
TITLE_COLOR   = '#1A237E'
SUBTITLE_COLOR = '#37474F'

plt.rcParams.update({
    'figure.facecolor'      : BG_COLOR,
    'axes.facecolor'        : BG_COLOR,
    'axes.edgecolor'        : '#B0BEC5',
    'axes.linewidth'        : 1.2,
    'axes.grid'             : True,
    'grid.color'            : GRID_COLOR,
    'grid.linewidth'        : 0.8,
    'grid.linestyle'        : '--',
    'font.family'           : 'sans-serif',
    'font.size'             : 11,
    'xtick.labelsize'       : 10,
    'ytick.labelsize'       : 10,
    'axes.labelsize'        : 12,
    'axes.labelweight'      : 'bold',
    'axes.labelcolor'       : SUBTITLE_COLOR,
    'xtick.color'           : SUBTITLE_COLOR,
    'ytick.color'           : SUBTITLE_COLOR,
    'legend.fontsize'       : 11,
    'figure.dpi'            : 150,
})

# =====================================================================
# 2. HÀM TIỆN ÍCH
# =====================================================================
def format_title(text): 
    # Loại bỏ số ở đầu chuỗi (nếu có vô tình truyền vào) và viết hoa toàn bộ
    import re
    clean_text = re.sub(r'^\d+[\.\-\:]?\s*', '', text)
    return clean_text.upper()

def apply_chart_title(ax, text, pad=40, fontsize=16):
    ax.set_title(format_title(text),
                 fontsize=fontsize, fontweight='bold',
                 pad=pad, color=TITLE_COLOR)

def percent_format(x, pos): 
    return f'{x:.1f}%'

def get_pretty_max(max_val):
    if pd.isna(max_val) or max_val <= 0 or not np.isfinite(max_val):
        return 10
    steps = [5, 10, 15, 20, 25, 30, 40, 50, 75, 100]
    for s in steps:
        if max_val <= s: return s
    return np.ceil(max_val / 10) * 10

def add_year_dividers(ax, labels):
    ylim = ax.get_ylim()
    for i, label in enumerate(labels):
        if '-01' in label or 'Q1' in label:
            ax.axvline(x=i, color='#90A4AE', linestyle='--', alpha=0.5, zorder=0)
            year_val = label.split('-')[0] if '-' in label else label[:4]
            ax.text(i + 0.3, ylim[1] * 0.97,
                    year_val, color='#607D8B',
                    fontsize=9, fontweight='bold', ha='left', va='top')

# =====================================================================
# 3. LOGIC BIỂU ĐỒ CHÍNH
# =====================================================================
def draw_chart_effective_discount(df_m):
    print("-> Đang xử lý: Phân tích xu hướng tỷ lệ chiết khấu thực tế...")
    
    # 1. Tiền xử lý dữ liệu (Feedback Hương)
    df = df_m.copy()
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['month_yr'] = df['order_date'].dt.to_period('M')
    
    df['promo_type'] = df['promo_type'].str.lower().str.strip()
    df['eff_rate'] = np.where(
        df['promo_type'] == 'percentage',
        df['discount_value'],
        (df['discount_amount'] / df['order_revenue'].replace(0, np.nan)) * 100
    )
    
    # Làm sạch dữ liệu
    df['eff_rate'] = df['eff_rate'].fillna(0).replace([np.inf, -np.inf], 0)
    df.loc[df['eff_rate'] > 100, 'eff_rate'] = 100

    # Gom nhóm
    monthly_data = df.groupby('month_yr')['eff_rate'].mean()
    x_lbl = monthly_data.index.astype(str)
    x_pos = np.arange(len(x_lbl))
    y_values = monthly_data.values

    # 2. Khởi tạo Figure & Axes
    fig, ax = plt.subplots(figsize=(22, 7))
    
    # Area fill & Line plot
    ax.fill_between(x_pos, y_values, color=VIBRANT[1], alpha=0.15)
    ax.plot(x_pos, y_values, color=VIBRANT[1],
            marker='o', markersize=6, linewidth=3,
            markerfacecolor='white', markeredgewidth=2,
            label='Tỷ lệ chiết khấu thực tế (%)')

    # 3. Cấu hình Trục Y
    p_max = get_pretty_max(y_values.max())
    ax.set_ylim(0, p_max)
    ax.set_yticks(np.linspace(0, p_max, 6))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(percent_format))
    ax.set_ylabel('Tỷ lệ chiết khấu (%)', labelpad=8)

    # 4. Cấu hình Trục X
    ax.set_xticks(x_pos[::3])
    ax.set_xticklabels(x_lbl[::3], rotation=90, fontsize=9)
    ax.set_xlabel('Tháng – Năm', labelpad=8)
    add_year_dividers(ax, x_lbl)

    # 5. Fix Legend: Đẩy ra ngoài đồ thị phía trên cùng, tránh che dữ liệu
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.02),
              ncol=1, frameon=True, shadow=True, fontsize=11)

    # 6. Tiêu đề chuẩn: KHÔNG SỐ, IN ĐẬM, VIẾT HOA
    apply_chart_title(ax, 'PHÂN TÍCH XU HƯỚNG TỶ LỆ CHIẾT KHẤU THỰC TẾ HÀNG THÁNG', pad=30)
    
    # 7. Tối ưu layout và lưu file
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    output_name = 'Effective_Discount_Rate_Trend.png'
    fig.savefig(os.path.join(CURRENT_DIR, output_name), dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"✅ Đã lưu biểu đồ thành công: {output_name}")


# =====================================================================
# 4. CHƯƠNG TRÌNH CHÍNH
# =====================================================================
def main():
    if not os.path.exists(PATH_MASTER):
        print(f"❌ LỖI: Không tìm thấy file tại {PATH_MASTER}")
        return
        
    try:
        df_master = pd.read_csv(PATH_MASTER, low_memory=False)
        draw_chart_effective_discount(df_master)
    except Exception as e:
        import traceback
        print(f"❌ LỖI HỆ THỐNG: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()