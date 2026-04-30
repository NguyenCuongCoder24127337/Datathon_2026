import argparse
import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# =====================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN
# =====================================================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
FILE_INPUT = os.path.join(BASE_DIR, 'data', 'master_data_final.csv')

# =====================================================================
# 2. BẢNG MÀU NỔI BẬT (VIBRANT PALETTE)
# =====================================================================
VIBRANT = [
    '#E63946', '#2196F3', '#FF9800', '#4CAF50', '#9C27B0', '#00BCD4',
    '#FF5722', '#3F51B5', '#FFEB3B', '#009688', '#F06292', '#8BC34A'
]

BG_COLOR       = '#FAFAFA'
GRID_COLOR     = '#E0E0E0'
TITLE_COLOR    = '#1A237E'
SUBTITLE_COLOR = '#37474F'

# =====================================================================
# 3. THIẾT LẬP THEME TOÀN CỤC
# =====================================================================
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

SHOW_VALUES = True

# =====================================================================
# 4. HÀM TIỆN ÍCH - SỬA LỖI VẠCH CHIA (TICKS)
# =====================================================================
def load_master_data() -> pd.DataFrame:
    if not os.path.exists(FILE_INPUT):
        raise FileNotFoundError(f"Không tìm thấy file: {FILE_INPUT}")
    return pd.read_csv(FILE_INPUT, low_memory=False)

def format_title(text): 
    clean_text = re.sub(r'^\d+[\.\-\:]?\s*', '', text)
    return clean_text.upper()

def apply_chart_title(ax, text, pad=40, fontsize=15):
    ax.set_title(format_title(text), fontsize=fontsize, fontweight='bold',
                 pad=pad, color=TITLE_COLOR)

def vn_format(x, pos=None):
    if pd.isna(x): return "0"
    val = float(x)
    abs_val = abs(val)
    sign = "-" if val < 0 else ""
    if abs_val >= 1e9: return f'{sign}{abs_val*1e-9:.1f} Tỷ'
    if abs_val >= 1e6: return f'{sign}{abs_val*1e-6:.0f} Tr'
    return f'{sign}{abs_val:,.0f}'

def percent_format(x, pos=None): 
    return f'{x:.1f}%'

def get_clean_ticks(max_val, n_ticks=6):
    """Tính toán vạch chia (ticks) cách đều nhau tuyệt đối và số đẹp"""
    if max_val <= 0 or pd.isna(max_val) or not np.isfinite(max_val): 
        return np.linspace(0, 5, n_ticks), 5
    
    intervals = n_ticks - 1
    raw_step = max_val / intervals
    mag = 10**np.floor(np.log10(raw_step)) if raw_step > 0 else 1
    res = raw_step / mag
    
    # Chọn bước nhảy "đẹp" gần nhất
    if res <= 1: clean_res = 1
    elif res <= 2: clean_res = 2
    elif res <= 2.5: clean_res = 2.5
    elif res <= 5: clean_res = 5
    else: clean_res = 10
    
    actual_step = clean_res * mag
    new_max = actual_step * intervals
    ticks = np.linspace(0, new_max, n_ticks)
    return ticks, new_max

def setup_pretty_dual_axes(ax1, ax2, max1, max2, y1_formatter=None, y2_formatter=None, keep_max2=False):
    """Đồng bộ vạch chia cho 2 trục Y để chúng khớp lưới nhau"""
    y1_ticks, y1_max = get_clean_ticks(max1, n_ticks=6)
    
    if keep_max2:
        # Dùng cho Pareto (max 100%)
        y2_max = max2
        y2_ticks = np.linspace(0, y2_max, 6)
    else:
        y2_ticks, y2_max = get_clean_ticks(max2, n_ticks=6)
        
    ax1.set_ylim(0, y1_max)
    ax1.yaxis.set_major_locator(ticker.FixedLocator(y1_ticks))
    
    ax2.set_ylim(0, y2_max)
    ax2.yaxis.set_major_locator(ticker.FixedLocator(y2_ticks))
    
    if y1_formatter: ax1.yaxis.set_major_formatter(ticker.FuncFormatter(y1_formatter))
    if y2_formatter: ax2.yaxis.set_major_formatter(ticker.FuncFormatter(y2_formatter))

def add_year_dividers(ax, labels):
    ylim = ax.get_ylim()
    for i, label in enumerate(labels):
        if '-01' in label or 'Q1' in label:
            ax.axvline(x=i, color='#90A4AE', linestyle='--', alpha=0.5, zorder=0)
            year_val = label.split('-')[0] if '-' in label else label[:4]
            ax.text(i + 0.3, ylim[1] * 0.97, year_val, color='#607D8B',
                    fontsize=9, fontweight='bold', ha='left', va='top')

# =====================================================================
# 5. CÁC HÀM VẼ BIỂU ĐỒ (ĐÃ FIX TRỤC Y)
# =====================================================================

def plot_pareto_revenue_by_category() -> str:
    print("-> 1: Pareto Doanh thu theo Danh mục...")
    df = load_master_data()
    cat_data = df.groupby("category", dropna=False)["order_revenue"].sum().sort_values(ascending=False).reset_index()
    cat_data["cum"] = (cat_data["order_revenue"].cumsum() / cat_data["order_revenue"].sum()) * 100
    n = len(cat_data)

    fig, ax1 = plt.subplots(figsize=(max(15, n * 1.6), 8))
    grad_colors = plt.cm.Blues(np.linspace(0.5, 0.9, n))
    bars = ax1.bar(range(n), cat_data["order_revenue"], color=grad_colors,
                   width=0.65, edgecolor='white', linewidth=1.5, alpha=0.9)

    for bar, val in zip(bars, cat_data["order_revenue"]):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + cat_data["order_revenue"].max() * 0.015,
                 vn_format(val), ha='center', va='bottom', fontsize=9, fontweight='bold', color=TITLE_COLOR)

    ax2 = ax1.twinx()
    ax2.plot(range(n), cat_data["cum"].values, color=VIBRANT[0],
             marker='D', markersize=8, linewidth=2.5,
             markerfacecolor=VIBRANT[0], markeredgecolor='white', markeredgewidth=1.5, zorder=5)
    
    ax2.axhline(80, color='#F44336', linestyle='--', linewidth=2, zorder=4)

    setup_pretty_dual_axes(ax1, ax2, cat_data["order_revenue"].max(), 100, 
                           y1_formatter=vn_format, y2_formatter=percent_format, keep_max2=True)
    
    ax1.set_xticks(range(n))
    ax1.set_xticklabels(cat_data["category"], rotation=30, ha='right', fontsize=10)
    ax1.set_xlabel('Danh mục sản phẩm (Category)', labelpad=8)
    ax1.set_ylabel('Tổng doanh thu (VND)', color='#1976D2', labelpad=8)
    ax2.set_ylabel('Tỷ lệ tích lũy (%)', color=VIBRANT[0], labelpad=8)
    ax2.grid(False)

    h1 = [Patch(facecolor='#1976D2', alpha=0.85, label='Doanh thu (VND)')]
    h2 = [Line2D([0], [0], color=VIBRANT[0], marker='D', linewidth=2, label='Tích lũy (%)')]
    h3 = [Line2D([0], [0], color='#F44336', linestyle='--', linewidth=2, label='Ngưỡng 80%')]
    fig.legend(handles=h1 + h2 + h3, loc='upper center', bbox_to_anchor=(0.5, 1.02),
               ncol=3, frameon=True, shadow=True, fontsize=11)

    apply_chart_title(ax1, 'Phân tích Pareto doanh thu theo danh mục sản phẩm', pad=35)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    
    out = os.path.join(CURRENT_DIR, '1_Pareto_Category.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    return out


def plot_category_revenue_and_order_count() -> str:
    print("-> 2: Doanh thu & Đơn hàng theo Danh mục...")
    df = load_master_data()
    cat_data = df.groupby("category").agg(
        order_revenue=("order_revenue", "sum"), 
        order_count=("order_id", "nunique")
    ).reset_index().sort_values("order_revenue", ascending=False)
    n = len(cat_data)

    fig, ax1 = plt.subplots(figsize=(max(15, n * 1.6), 8))
    bars = ax1.bar(range(n), cat_data["order_revenue"], color=VIBRANT[1],
                   width=0.6, edgecolor='white', linewidth=1.5, alpha=0.85)

    for bar, val in zip(bars, cat_data["order_revenue"]):
        if val == 0: continue
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + cat_data["order_revenue"].max() * 0.015,
                 vn_format(val), ha='center', va='bottom', fontsize=9, fontweight='bold', color=TITLE_COLOR)

    ax2 = ax1.twinx()
    ax2.plot(range(n), cat_data["order_count"].values, color=VIBRANT[6],
             marker='o', markersize=8, linewidth=2.5,
             markerfacecolor='white', markeredgewidth=2, zorder=5)
    
    for i, val in enumerate(cat_data["order_count"].values):
        ax2.text(i, val + cat_data["order_count"].max() * 0.04, f'{val:,.0f}',
                 ha='center', va='bottom', fontsize=9, fontweight='bold', color=VIBRANT[6])

    setup_pretty_dual_axes(ax1, ax2, cat_data["order_revenue"].max(), cat_data["order_count"].max(),
                           y1_formatter=vn_format, y2_formatter=lambda x, p: f'{x:,.0f}')
    
    ax1.set_xticks(range(n))
    ax1.set_xticklabels(cat_data["category"], rotation=30, ha='right', fontsize=10)
    ax1.set_xlabel('Danh mục sản phẩm (Category)', labelpad=8)
    ax1.set_ylabel('Tổng doanh thu (VND)', color=VIBRANT[1], labelpad=8)
    ax2.set_ylabel('Số lượng đơn hàng', color=VIBRANT[6], labelpad=8)
    ax2.grid(False)

    h1 = [Patch(facecolor=VIBRANT[1], alpha=0.85, label='Doanh thu (VND)')]
    h2 = [Line2D([0], [0], color=VIBRANT[6], marker='o', linewidth=2, label='Số lượng đơn hàng')]
    fig.legend(handles=h1 + h2, loc='upper center', bbox_to_anchor=(0.5, 1.02),
               ncol=2, frameon=True, shadow=True, fontsize=11)

    apply_chart_title(ax1, 'Hiệu quả kinh doanh theo danh mục: Doanh thu và Số đơn', pad=35)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    
    out = os.path.join(CURRENT_DIR, '2_Category_Rev_Orders.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    return out


def plot_revenue_and_profit_by_quarter() -> str:
    print("-> 3: Doanh thu & Lợi nhuận theo Quý...")
    df = load_master_data()
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["quarter_period"] = df["order_date"].dt.to_period("Q")
    q_data = df.groupby("quarter_period")[["order_revenue", "order_profit"]].sum().reset_index()
    x_lbl = q_data["quarter_period"].astype(str).tolist()
    x_pos = np.arange(len(q_data))

    fig, ax = plt.subplots(figsize=(22, 7))
    
    ax.plot(x_pos, q_data["order_revenue"], color=VIBRANT[1], marker='o', markersize=6, 
            linewidth=2.5, markerfacecolor='white', markeredgewidth=2, label='Tổng Doanh Thu')
    ax.plot(x_pos, q_data["order_profit"], color=VIBRANT[0], marker='s', markersize=6, 
            linewidth=2.5, markerfacecolor='white', markeredgewidth=2, label='Tổng Lợi Nhuận')

    ax.axhline(0, color='#90A4AE', linewidth=1.5, linestyle='--')
    
    # Ép vạch chia cách đều
    y_ticks, y_max = get_clean_ticks(q_data["order_revenue"].max(), n_ticks=6)
    ymin_val = q_data["order_profit"].min()
    ymin = ymin_val * 1.2 if ymin_val < 0 else 0
    
    ax.set_ylim(ymin, y_max)
    ax.yaxis.set_major_locator(ticker.FixedLocator(y_ticks))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(vn_format))

    if SHOW_VALUES:
        for i, row in q_data.iterrows():
            ax.text(i, row["order_revenue"] + y_max * 0.03, vn_format(row["order_revenue"]), 
                    ha='center', va='bottom', fontsize=9, fontweight='bold', color=VIBRANT[1])
            y_offset = -y_max * 0.04 if row["order_profit"] >= 0 else y_max * 0.04
            va = 'top' if row["order_profit"] >= 0 else 'bottom'
            ax.text(i, row["order_profit"] + y_offset, vn_format(row["order_profit"]), 
                    ha='center', va=va, fontsize=9, fontweight='bold', color=VIBRANT[0])

    add_year_dividers(ax, x_lbl)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x_lbl, rotation=90, fontsize=9)
    ax.set_xlabel('Thời gian (Quý - Năm)', labelpad=8)
    ax.set_ylabel('Giá trị (VND)', labelpad=8)

    fig.legend(handles=ax.get_lines()[:2], loc='upper center', bbox_to_anchor=(0.5, 1.02),
               ncol=2, frameon=True, shadow=True, fontsize=11)

    apply_chart_title(ax, 'Phân tích hiệu quả tài chính doanh thu và lợi nhuận theo quý', pad=35)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    
    out = os.path.join(CURRENT_DIR, '3_Quarterly_Performance.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    return out


def plot_revenue_and_profit_by_year() -> str:
    print("-> 4: Doanh thu & Lợi nhuận theo Năm...")
    df = load_master_data()
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["year"] = df["order_date"].dt.year
    y_data = df.groupby("year")[["order_revenue", "order_profit"]].sum().reset_index()
    x_pos = y_data["year"].tolist()

    fig, ax = plt.subplots(figsize=(15, 7))
    
    ax.plot(x_pos, y_data["order_revenue"], color=VIBRANT[1], marker='o', markersize=7, 
            linewidth=2.5, markerfacecolor='white', markeredgewidth=2, label='Tổng Doanh Thu')
    ax.plot(x_pos, y_data["order_profit"], color=VIBRANT[0], marker='s', markersize=7, 
            linewidth=2.5, markerfacecolor='white', markeredgewidth=2, label='Tổng Lợi Nhuận')

    ax.axhline(0, color='#90A4AE', linewidth=1.5, linestyle='--')
    
    y_ticks, y_max = get_clean_ticks(y_data["order_revenue"].max(), n_ticks=6)
    ymin_val = y_data["order_profit"].min()
    ymin = ymin_val * 1.2 if ymin_val < 0 else 0

    ax.set_ylim(ymin, y_max)
    ax.yaxis.set_major_locator(ticker.FixedLocator(y_ticks))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(vn_format))

    if SHOW_VALUES:
        for i, row in y_data.iterrows():
            ax.text(row["year"], row["order_revenue"] + y_max * 0.03, vn_format(row["order_revenue"]), 
                    ha='center', va='bottom', fontsize=9, fontweight='bold', color=VIBRANT[1])
            y_offset = -y_max * 0.04 if row["order_profit"] >= 0 else y_max * 0.04
            va = 'top' if row["order_profit"] >= 0 else 'bottom'
            ax.text(row["year"], row["order_profit"] + y_offset, vn_format(row["order_profit"]), 
                    ha='center', va=va, fontsize=9, fontweight='bold', color=VIBRANT[0])

    ax.set_xticks(x_pos)
    ax.set_xlabel('Năm (Year)', labelpad=8)
    ax.set_ylabel('Giá trị (VND)', labelpad=8)

    fig.legend(handles=ax.get_lines()[:2], loc='upper center', bbox_to_anchor=(0.5, 1.02),
               ncol=2, frameon=True, shadow=True, fontsize=11)

    apply_chart_title(ax, 'Hiệu quả tài chính doanh thu và lợi nhuận theo năm', pad=35)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    
    out = os.path.join(CURRENT_DIR, '4_Yearly_Performance.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    return out


def plot_revenue_by_quarter_10_years() -> str:
    print("-> 5: Xu hướng Quý so sánh 10 Năm...")
    df = load_master_data()
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["year"] = df["order_date"].dt.year
    df["quarter"] = df["order_date"].dt.quarter
    g_data = df.groupby(["year", "quarter"])["order_revenue"].sum().reset_index()

    fig, ax = plt.subplots(figsize=(15, 7))
    years = sorted(g_data["year"].unique())
    
    lines = []
    for i, year in enumerate(years):
        year_data = g_data[g_data["year"] == year].sort_values("quarter")
        color = VIBRANT[i % len(VIBRANT)]
        line, = ax.plot(year_data["quarter"], year_data["order_revenue"], 
                        color=color, marker='o', markersize=6, linewidth=2.2, 
                        markerfacecolor='white', markeredgewidth=1.5, label=str(year))
        lines.append(line)

    y_ticks, y_max = get_clean_ticks(g_data["order_revenue"].max(), n_ticks=6)
    ax.set_ylim(0, y_max)
    ax.yaxis.set_major_locator(ticker.FixedLocator(y_ticks))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(vn_format))
    
    ax.set_xticks([1, 2, 3, 4])
    ax.set_xticklabels(["Quý 1", "Quý 2", "Quý 3", "Quý 4"], fontsize=11)
    ax.set_xlabel('Quý Tài Chính', labelpad=8)
    ax.set_ylabel('Tổng Doanh Thu (VND)', labelpad=8)

    fig.legend(handles=lines, loc='upper center', bbox_to_anchor=(0.5, 1.02),
               ncol=min(len(years), 10), frameon=True, shadow=True, fontsize=10)

    apply_chart_title(ax, 'Xu hướng doanh thu theo quý so sánh 10 năm', pad=35)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    
    out = os.path.join(CURRENT_DIR, '5_Quarterly_10Y_Trend.png')
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    return out

def run_all_charts() -> None:
    outputs = [
        plot_pareto_revenue_by_category(),
        plot_category_revenue_and_order_count(),
        plot_revenue_and_profit_by_quarter(),
        plot_revenue_and_profit_by_year(),
        plot_revenue_by_quarter_10_years(),
    ]
    print("\n" + "="*55)
    print("✅ HOÀN TẤT! Đã kết xuất xong bộ biểu đồ VIBRANT.")
    print("="*55)

def main() -> None:
    parser = argparse.ArgumentParser(description="Trình render biểu đồ Vibrant Master.")
    parser.add_argument("--chart", choices=["all", "pareto", "category", "quarter", "year", "quarter-10y"],
                        default="all", help="Chọn biểu đồ cần vẽ.")
    args = parser.parse_args()

    runners = {
        "pareto": plot_pareto_revenue_by_category,
        "category": plot_category_revenue_and_order_count,
        "quarter": plot_revenue_and_profit_by_quarter,
        "year": plot_revenue_and_profit_by_year,
        "quarter-10y": plot_revenue_by_quarter_10_years,
    }

    print("--- KHỞI ĐỘNG HỆ THỐNG RENDER (VIBRANT PURE MATPLOTLIB) ---")
    try:
        if args.chart == "all":
            run_all_charts()
        else:
            out = runners[args.chart]()
            print(f"✅ Đã lưu: {out}")
    except Exception as e:
        import traceback
        print(f"❌ LỖI: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()