import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import matplotlib.ticker as ticker
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# =====================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN
# =====================================================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)

PATH_MASTER  = os.path.join(BASE_DIR, 'data', 'master_data_final.csv')
PATH_TRAFFIC = os.path.join(BASE_DIR, 'data_processed', 'web_traffic_processed.csv')

# =====================================================================
# 2. BẢNG MÀU NỔI BẬT (VIBRANT PALETTE)
# =====================================================================
# 12 màu nổi, đủ tương phản, phù hợp báo cáo chuyên nghiệp
VIBRANT = [
    '#E63946',  # 0  đỏ san hô
    '#2196F3',  # 1  xanh dương cobalt
    '#FF9800',  # 2  cam amber
    '#4CAF50',  # 3  xanh lá emerald
    '#9C27B0',  # 4  tím violet
    '#00BCD4',  # 5  cyan teal
    '#FF5722',  # 6  đỏ cam deep-orange
    '#3F51B5',  # 7  indigo
    '#FFEB3B',  # 8  vàng canary  (dùng cho fill nhạt)
    '#009688',  # 9  teal đậm
    '#F06292',  # 10 hồng pastel đậm
    '#8BC34A',  # 11 xanh lá lime
]

# Màu nền / viền nhẹ
BG_COLOR      = '#FAFAFA'
GRID_COLOR    = '#E0E0E0'
TITLE_COLOR   = '#1A237E'      # navy đậm
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
    'legend.fontsize'       : 10,
    'legend.framealpha'     : 0.95,
    'legend.edgecolor'      : '#B0BEC5',
    'figure.dpi'            : 150,
})

# =====================================================================
# 4. HÀM TIỆN ÍCH
# =====================================================================
def format_title(text): return text.upper()

def apply_chart_title(ax, text, pad=40, fontsize=15):
    ax.set_title(format_title(text),
                 fontsize=fontsize, fontweight='bold',
                 pad=pad, color=TITLE_COLOR)

def vn_format(x, pos):
    if abs(x) >= 1e9: return f'{x*1e-9:.1f} Tỷ'
    if abs(x) >= 1e6: return f'{x*1e-6:.0f} Tr'
    return f'{x:,.0f}'

def percent_format(x, pos): return f'{x:.1f}%'

def get_pretty_max(max_val):
    if pd.isna(max_val) or max_val <= 0 or not np.isfinite(max_val):
        return 10
    try:
        exponent = np.floor(np.log10(abs(max_val)))
        if not np.isfinite(exponent): return 10
        fraction = max_val / (10**exponent)
    except Exception: return 10
    steps = [1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10]
    clean_frac = next((s for s in steps if fraction <= s), 10)
    result = clean_frac * (10**exponent)
    return result if np.isfinite(result) and result > 0 else 10

def setup_pretty_dual_axes(ax1, ax2, max1, max2,
                           y1_formatter=None, y2_formatter=None,
                           keep_max2=False):
    p_max1 = get_pretty_max(max1)
    p_max2 = max2 if keep_max2 else get_pretty_max(max2)
    for v in [p_max1, p_max2]:
        if not np.isfinite(v) or v <= 0: v = 10
    ax1.set_ylim(0, p_max1); ax2.set_ylim(0, p_max2)
    ax1.set_yticks(np.linspace(0, p_max1, 6))
    ax2.set_yticks(np.linspace(0, p_max2, 6))
    if y1_formatter: ax1.yaxis.set_major_formatter(ticker.FuncFormatter(y1_formatter))
    if y2_formatter: ax2.yaxis.set_major_formatter(ticker.FuncFormatter(y2_formatter))

def add_year_dividers(ax, labels):
    ylim = ax.get_ylim()
    for i, label in enumerate(labels):
        if '-01' in label or 'Q1' in label:
            ax.axvline(x=i, color='#90A4AE', linestyle='--', alpha=0.5, zorder=0)
            year_val = label.split('-')[0] if '-' in label else label[:4]
            ax.text(i + 0.3, ylim[1] * 0.97,
                    year_val, color='#607D8B',
                    fontsize=9, fontweight='bold', ha='left', va='top')

def smart_bar_label(ax, bars, formatter=None, fontsize=9, rotation=0,
                    padding=4, color='#1A237E'):
    """Bar label thông minh: bỏ qua label = 0, căn chỉnh tránh tràn"""
    for bar in bars:
        h = bar.get_height() if hasattr(bar, 'get_height') else bar.get_width()
        if h == 0 or not np.isfinite(h): continue
        if hasattr(bar, 'get_height'):
            x, y = bar.get_x() + bar.get_width() / 2, h
            va, ha = 'bottom', 'center'
        else:
            x, y = h, bar.get_y() + bar.get_height() / 2
            va, ha = 'center', 'left'
        label = formatter(h) if formatter else f'{h:,.0f}'
        ax.text(x, y + padding * 0.01 * ax.get_ylim()[1] if hasattr(bar, 'get_height') else y,
                label, ha=ha, va=va,
                fontsize=fontsize, fontweight='bold', color=color, rotation=rotation)

# =====================================================================
# 5. 13 BIỂU ĐỒ – LOGIC GIỮ NGUYÊN, STYLE NÂNG CẤP
# =====================================================================

def draw_chart_1(df_m, df_t):
    print("-> 1: Phễu chuyển đổi...")
    total_s = df_t['sessions'].sum()
    eng_s   = ((1 - df_t['bounce_rate']) * df_t['sessions']).sum()
    orders  = df_m['order_id'].nunique()
    data = pd.DataFrame({
        'Bước'    : ['1. Tổng truy cập\n(Sessions)', '2. Đã tương tác\n(Engaged Sessions)', '3. Đã đặt hàng\n(Orders)'],
        'Số lượng': [total_s, eng_s, orders]
    })

    fig, ax = plt.subplots(figsize=(13, 6))
    colors = [VIBRANT[1], VIBRANT[2], VIBRANT[0]]
    bars = ax.barh(data['Bước'], data['Số lượng'], color=colors,
                   height=0.55, edgecolor='white', linewidth=1.5)

    ax.xaxis.set_major_formatter(ticker.FuncFormatter(vn_format))
    for bar, val in zip(bars, data['Số lượng']):
        ax.text(val + total_s * 0.01, bar.get_y() + bar.get_height() / 2,
                vn_format(val, None), va='center', ha='left',
                fontsize=11, fontweight='bold', color=TITLE_COLOR)

    ax.set_xlabel('Số lượng (Phiên / Đơn hàng)', labelpad=8)
    ax.set_ylabel('Giai đoạn phễu', labelpad=8)
    ax.set_xlim(0, total_s * 1.18)
    apply_chart_title(ax, 'Phễu chuyển đổi: Awareness → Purchase', pad=20)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(CURRENT_DIR, '1_Conversion_Funnel.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)


def draw_chart_2(df_m, df_t):
    print("-> 2: CV Rate theo Traffic Source...")
    t    = df_t.groupby('traffic_source')['sessions'].sum()
    o    = df_m.groupby('order_source')['order_id'].nunique()
    data = pd.DataFrame({'s': t, 'o': o}).fillna(0)
    data['cv'] = (data['o'] / data['s'] * 100).replace([np.inf, -np.inf], 0).fillna(0)
    data = data.sort_values('cv', ascending=True)

    fig, ax = plt.subplots(figsize=(13, 7))
    cmap_vals = np.linspace(0.3, 0.9, len(data))
    bar_colors = plt.cm.RdYlGn(cmap_vals)
    bars = ax.barh(data.index, data['cv'], color=bar_colors,
                   height=0.6, edgecolor='white', linewidth=1.2)

    for bar, val in zip(bars, data['cv']):
        ax.text(val + 0.05, bar.get_y() + bar.get_height() / 2,
                f'{val:.2f}%', va='center', ha='left',
                fontsize=10, fontweight='bold', color=TITLE_COLOR)

    ax.set_xlabel('Tỷ lệ chuyển đổi (%)', labelpad=8)
    ax.set_ylabel('Nguồn truy cập (Traffic Source)', labelpad=8)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(percent_format))
    ax.set_xlim(0, data['cv'].max() * 1.2)
    apply_chart_title(ax, 'Tỷ lệ chuyển đổi theo nguồn truy cập (%)', pad=20)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(CURRENT_DIR, '2_Conversion_Rate_by_Traffic_Source.png'),
                dpi=300, bbox_inches='tight')
    plt.close(fig)


def draw_chart_3(df_m, df_t):
    print("-> 3: Xu hướng CV Rate 10 năm...")
    
    # --- 1. Xử lý dữ liệu (Chống lỗi Inf/NaN) ---
    t = df_t.groupby(df_t['date'].dt.to_period('M'))['sessions'].sum()
    o = df_m.groupby(df_m['order_date'].dt.to_period('M'))['order_id'].nunique()
    
    data = pd.DataFrame({'s': t, 'o': o}).fillna(0)
    # Tránh chia cho 0 và xử lý giá trị vô cực
    data['cv'] = (data['o'] / data['s'].replace(0, np.nan) * 100).fillna(0)
    data['cv'] = data['cv'].replace([np.inf, -np.inf], 0)
    
    x_lbl = data.index.astype(str)
    x_pos = np.arange(len(x_lbl))

    fig, ax = plt.subplots(figsize=(22, 7))

    # --- 2. Tính toán vạch chia ĐỀU TUYỆT ĐỐI ---
    def get_clean_ticks(max_val, n_ticks=6):
        if max_val <= 0 or pd.isna(max_val): 
            return np.linspace(0, 5, n_ticks), 5
        
        # Tìm bước nhảy thô
        raw_step = max_val / (n_ticks - 1)
        # Tìm lũy thừa của 10 gần nhất
        mag = 10**np.floor(np.log10(raw_step)) if raw_step > 0 else 1
        res = raw_step / mag
        
        # Chọn bước nhảy "đẹp" (1, 2, 2.5, 5, 10)
        if res <= 1: clean_res = 1
        elif res <= 2: clean_res = 2
        elif res <= 2.5: clean_res = 2.5
        elif res <= 5: clean_res = 5
        else: clean_res = 10
        
        actual_step = clean_res * mag
        new_max = actual_step * (n_ticks - 1)
        ticks = np.arange(0, new_max + actual_step/2, actual_step)
        return ticks, new_max

    # Áp dụng tính toán vạch chia (mặc định 6 vạch cho đẹp)
    y_ticks, y_max = get_clean_ticks(data['cv'].max(), n_ticks=6)

    # --- 3. Vẽ biểu đồ ---
    ax.fill_between(x_pos, data['cv'].values, color=VIBRANT[1], alpha=0.15)
    ax.plot(x_pos, data['cv'].values, color=VIBRANT[1],
            marker='o', markersize=3.5, linewidth=2,
            markerfacecolor='white', markeredgewidth=1.5,
            label='Tỷ lệ chuyển đổi (%)')

    # --- 4. Cấu hình trục Y (Ép cách đều) ---
    ax.set_ylim(0, y_max)
    ax.set_yticks(y_ticks)
    ax.yaxis.set_major_locator(ticker.FixedLocator(y_ticks))
    # Sử dụng formatter của bạn (percent_format)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: percent_format(x, p)))

    # --- 5. Cấu hình trục X & Thẩm mỹ ---
    ax.set_xticks(x_pos[::3])
    ax.set_xticklabels(x_lbl[::3], rotation=90, fontsize=9)
    
    if 'add_year_dividers' in globals():
        add_year_dividers(ax, x_lbl)
        
    ax.set_xlabel('Tháng – Năm', labelpad=8)
    ax.set_ylabel('Tỷ lệ chuyển đổi (%)', labelpad=8)
    ax.legend(loc='upper left', framealpha=0.9)
    
    if 'apply_chart_title' in globals():
        apply_chart_title(ax, 'Xu hướng tỷ lệ chuyển đổi hàng tháng (10 năm)', pad=25)
    
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(CURRENT_DIR, '3_Monthly_Conversion_Rate_Trend.png'),
                dpi=300, bbox_inches='tight')
    plt.close(fig)


def draw_chart_4(df_m):
    print("-> 4: Xu hướng Khuyến mãi...")
    p    = df_m[df_m['promo_type'].str.contains('percentage', na=False, case=False)]
    data = p.groupby(p['order_date'].dt.to_period('M'))['discount_value'].sum()
    x_lbl = data.index.astype(str)
    x_pos = np.arange(len(x_lbl))

    fig, ax = plt.subplots(figsize=(22, 7))
    ax.fill_between(x_pos, data.values, color=VIBRANT[2], alpha=0.2)
    ax.plot(x_pos, data.values, color=VIBRANT[2],
            marker='o', markersize=3.5, linewidth=2,
            markerfacecolor='white', markeredgewidth=1.5,
            label='Giá trị khuyến mãi (VND)')

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(vn_format))
    ax.set_xticks(x_pos[::3]); ax.set_xticklabels(x_lbl[::3], rotation=90, fontsize=9)
    add_year_dividers(ax, x_lbl)
    ax.set_xlabel('Tháng – Năm', labelpad=8)
    ax.set_ylabel('Tổng giá trị khuyến mãi (VND)', labelpad=8)
    ax.legend(loc='upper left', framealpha=0.9)
    apply_chart_title(ax, 'Tổng giá trị khuyến mãi hàng tháng (VND)', pad=25)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(CURRENT_DIR, '4_Monthly_Promotion_Trend.png'),
                dpi=300, bbox_inches='tight')
    plt.close(fig)


def draw_chart_5(df_m, df_t):
    print("-> 5: Khuyến mãi & CV Rate theo Quý...")
    p    = df_m.groupby(df_m['order_date'].dt.to_period('Q'))['discount_value'].sum()
    o    = df_m.groupby(df_m['order_date'].dt.to_period('Q'))['order_id'].nunique()
    s    = df_t.groupby(df_t['date'].dt.to_period('Q'))['sessions'].sum()
    data = pd.DataFrame({'p': p, 'o': o, 's': s}).fillna(0)
    data['cv'] = (data['o'] / data['s'] * 100).replace([np.inf, -np.inf], 0).fillna(0)

    if data['p'].max() <= 0 and data['cv'].max() <= 0:
        print("⚠️ Chart 5: Không có dữ liệu, bỏ qua."); return

    x_lbl = data.index.astype(str)
    x_pos = np.arange(len(x_lbl))

    fig, ax1 = plt.subplots(figsize=(20, 8))
    ax1.fill_between(x_pos, data['p'].values, color=VIBRANT[4], alpha=0.25, label='Khuyến mãi (VND)')
    ax1.plot(x_pos, data['p'].values, color=VIBRANT[4], linewidth=1.5, alpha=0.6)

    ax2 = ax1.twinx()
    ax2.plot(x_pos, data['cv'].values, color=VIBRANT[0],
             marker='o', markersize=6, linewidth=2.5,
             markerfacecolor='white', markeredgewidth=2,
             label='Tỷ lệ chuyển đổi (%)')

    setup_pretty_dual_axes(ax1, ax2,
                           max(data['p'].max(), 1), max(data['cv'].max(), 1),
                           y1_formatter=vn_format, y2_formatter=percent_format)

    ax1.set_xticks(range(len(x_lbl)))
    ax1.set_xticklabels(x_lbl, rotation=90, fontsize=9)
    add_year_dividers(ax1, x_lbl)
    ax1.set_xlabel('Quý – Năm', labelpad=8)
    ax1.set_ylabel('Tổng giá trị khuyến mãi (VND)', color=VIBRANT[4], labelpad=8)
    ax2.set_ylabel('Tỷ lệ chuyển đổi (%)', color=VIBRANT[0], labelpad=8)
    ax1.tick_params(axis='y', colors=VIBRANT[4])
    ax2.tick_params(axis='y', colors=VIBRANT[0])

    h1 = [Patch(facecolor=VIBRANT[4], alpha=0.5, label='Khuyến mãi (VND)')]
    h2 = [Line2D([0], [0], color=VIBRANT[0], marker='o', linewidth=2, label='Tỷ lệ CV (%)')]
    # Legend đặt ngoài vùng vẽ – phía trên góc phải, không che dữ liệu
    fig.legend(handles=h1 + h2,
               loc='upper center', bbox_to_anchor=(0.5, 1.02),
               ncol=2, frameon=True, shadow=True, fontsize=11)

    apply_chart_title(ax1, 'Tương quan khuyến mãi và tỷ lệ chuyển đổi theo quý', pad=30)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(os.path.join(CURRENT_DIR, '5_Promo_vs_CVRate_Quarterly.png'),
                dpi=300, bbox_inches='tight')
    plt.close(fig)


def draw_chart_6(df_t):
    print("-> 6: Pageviews Trend...")
    data  = df_t.groupby(df_t['date'].dt.to_period('M'))['page_views'].sum()
    x_lbl = data.index.astype(str)
    x_pos = np.arange(len(x_lbl))

    fig, ax = plt.subplots(figsize=(22, 7))
    ax.fill_between(x_pos, data.values, color=VIBRANT[9], alpha=0.2)
    ax.plot(x_pos, data.values, color=VIBRANT[9],
            marker='o', markersize=3.5, linewidth=2,
            markerfacecolor='white', markeredgewidth=1.5,
            label='Tổng pageviews')

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(vn_format))
    ax.set_xticks(x_pos[::3]); ax.set_xticklabels(x_lbl[::3], rotation=90, fontsize=9)
    add_year_dividers(ax, x_lbl)
    ax.set_xlabel('Tháng – Năm', labelpad=8)
    ax.set_ylabel('Tổng lượt xem trang (Pageviews)', labelpad=8)
    ax.legend(loc='upper left', framealpha=0.9)
    apply_chart_title(ax, 'Xu hướng tổng pageviews hàng tháng', pad=25)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(CURRENT_DIR, '6_Total_Pageviews_Trend.png'),
                dpi=300, bbox_inches='tight')
    plt.close(fig)


def draw_chart_7(df_m, df_t):
    print("-> 7: Pageviews & CV Rate...")
    
    # --- 1. Logic dữ liệu (Giữ nguyên) ---
    pv = df_t.groupby(df_t['date'].dt.to_period('M'))['page_views'].sum()
    o  = df_m.groupby(df_m['order_date'].dt.to_period('M'))['order_id'].nunique()
    s  = df_t.groupby(df_t['date'].dt.to_period('M'))['sessions'].sum()
    
    data = pd.DataFrame({'pv': pv, 'o': o, 's': s}).fillna(0)
    data['cv'] = (data['o'] / data['s'].replace(0, np.nan) * 100).fillna(0)
    data['cv'] = data['cv'].replace([np.inf, -np.inf], 0)
    
    x_lbl = data.index.astype(str)
    x_pos = np.arange(len(x_lbl))

    fig, ax1 = plt.subplots(figsize=(22, 8))

    # --- 2. Hàm tính toán vạch chia "SỐ ĐẸP" (Key fix) ---
    def get_clean_ticks(max_val, n_ticks=6):
        """Đảm bảo bước nhảy là số tròn (1, 2, 5, 10...) để không bị lỗi 0 1 2 4"""
        if max_val <= 0 or pd.isna(max_val): 
            return np.linspace(0, 5, n_ticks), 5
        
        # Tìm bước nhảy thô
        raw_step = max_val / (n_ticks - 1)
        # Tìm lũy thừa của 10 gần nhất
        mag = 10**np.floor(np.log10(raw_step)) if raw_step > 0 else 1
        res = raw_step / mag
        
        # Chọn bước nhảy "đẹp" gần nhất
        if res <= 1: clean_res = 1
        elif res <= 2: clean_res = 2
        elif res <= 2.5: clean_res = 2.5
        elif res <= 5: clean_res = 5
        else: clean_res = 10
        
        actual_step = clean_res * mag
        new_max = actual_step * (n_ticks - 1)
        ticks = np.arange(0, new_max + actual_step/2, actual_step)
        return ticks, new_max

    # Áp dụng cho cả 2 trục với cùng số lượng vạch (6 vạch = 5 khoảng)
    y1_ticks, y1_max = get_clean_ticks(data['pv'].max(), n_ticks=6)
    y2_ticks, y2_max = get_clean_ticks(data['cv'].max(), n_ticks=6)

    # --- 3. Vẽ biểu đồ ---
    ax1.plot(x_pos, data['pv'].values, color=VIBRANT[7],
             marker='o', markersize=3.5, linewidth=2,
             markerfacecolor='white', markeredgewidth=1.5, label='Pageviews')
    
    ax2 = ax1.twinx()
    ax2.plot(x_pos, data['cv'].values, color=VIBRANT[6],
             marker='s', markersize=3.5, linewidth=2,
             markerfacecolor='white', markeredgewidth=1.5, label='Tỷ lệ CV (%)')

    # --- 4. Cấu hình trục Y (Bắt buộc dùng FixedLocator) ---
    ax1.set_ylim(0, y1_max)
    ax1.set_yticks(y1_ticks)
    ax1.yaxis.set_major_locator(ticker.FixedLocator(y1_ticks))
    
    ax2.set_ylim(0, y2_max)
    ax2.set_yticks(y2_ticks)
    ax2.yaxis.set_major_locator(ticker.FixedLocator(y2_ticks))

    # Định dạng nhãn (vn_format và percent_format)
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(vn_format))
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(percent_format))

    # --- 5. Thẩm mỹ (Giữ nguyên logic cũ của bạn) ---
    ax1.set_xticks(x_pos[::3])
    ax1.set_xticklabels(x_lbl[::3], rotation=90, fontsize=9)
    if 'add_year_dividers' in globals():
        add_year_dividers(ax1, x_lbl)
    
    ax1.set_xlabel('Tháng – Năm', labelpad=8)
    ax1.set_ylabel('Tổng lượt xem trang (Pageviews)', color=VIBRANT[7], labelpad=8)
    ax2.set_ylabel('Tỷ lệ chuyển đổi (%)', color=VIBRANT[6], labelpad=8)
    
    ax1.tick_params(axis='y', colors=VIBRANT[7])
    ax2.tick_params(axis='y', colors=VIBRANT[6])
    
    ax1.grid(True, axis='y', alpha=0.3, linestyle='--')
    ax2.grid(False)

    # Legend
    h1 = [Line2D([0], [0], color=VIBRANT[7], marker='o', linewidth=2, label='Pageviews')]
    h2 = [Line2D([0], [0], color=VIBRANT[6], marker='s', linewidth=2, label='Tỷ lệ CV (%)')]
    fig.legend(handles=h1 + h2, loc='upper center', bbox_to_anchor=(0.5, 1.02),
               ncol=2, frameon=True, shadow=True, fontsize=11)

    if 'apply_chart_title' in globals():
        apply_chart_title(ax1, 'Tương quan pageviews và tỷ lệ chuyển đổi hàng tháng', pad=30)
    
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(os.path.join(CURRENT_DIR, '7_Pageviews_vs_CVRate_Monthly.png'),
                dpi=300, bbox_inches='tight')
    plt.close(fig)


def draw_chart_8(df_m, df_t):
    print("-> 8: Orders & CV Rate by Source...")
    
    # --- 1. Xử lý dữ liệu (Chống lỗi chia cho 0) ---
    o = df_m.groupby('order_source')['order_id'].nunique()
    s = df_t.groupby('traffic_source')['sessions'].sum()
    data = pd.DataFrame({'o': o, 's': s}).fillna(0)
    
    # Tránh chia cho 0 để không bị Inf
    data['cv'] = (data['o'] / data['s'].replace(0, np.nan) * 100).fillna(0)
    data = data.sort_values('o', ascending=False)
    n = len(data)

    fig, ax1 = plt.subplots(figsize=(max(13, n * 1.6), 8))
    
    # --- 2. Vẽ Bars (Số đơn hàng) ---
    bar_colors = [VIBRANT[i % len(VIBRANT)] for i in range(n)]
    bars = ax1.bar(range(n), data['o'], color=bar_colors,
                    width=0.6, edgecolor='white', linewidth=1.5, alpha=0.7,
                    label='Số đơn hàng')

    # Label cho Bar
    for bar, val in zip(bars, data['o']):
        if val == 0: continue
        ax1.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + data['o'].max() * 0.01,
                 f'{val:,.0f}', ha='center', va='bottom',
                 fontsize=9, fontweight='bold', color=TITLE_COLOR)

    # --- 3. Vẽ Line (CV Rate) ---
    ax2 = ax1.twinx()
    ax2.plot(range(n), data['cv'].values, color=VIBRANT[0],
             marker='D', markersize=8, linewidth=2.5,
             markerfacecolor=VIBRANT[0], markeredgecolor='white', markeredgewidth=1.5,
             label='Tỷ lệ CV (%)', zorder=5)

    # --- 4. Sửa lỗi hiển thị Text trên Line ---
    for i, val in enumerate(data['cv'].values):
        # f'{val:.2f}%': Làm tròn 2 chữ số thập phân
        # bbox: Tạo khung nền trắng mờ phía sau chữ để không bị background che khuất
        ax2.text(i, val + data['cv'].max() * 0.03, f'{val:.2f}%',
                 ha='center', va='bottom', 
                 fontsize=10, fontweight='bold', color=VIBRANT[0],
                 zorder=10,
                 bbox=dict(facecolor='white', alpha=0.6, edgecolor='none', pad=1))

    # --- 5. Đồng bộ vạch chia (Để đảm bảo thẩm mỹ như các biểu đồ trước) ---
    if 'setup_pretty_dual_axes' in globals():
        setup_pretty_dual_axes(ax1, ax2, data['o'].max(), data['cv'].max(),
                               y1_formatter=lambda x, p: f'{x:,.0f}',
                               y2_formatter=percent_format)
    
    # Thiết lập trục X
    ax1.set_xticks(range(n))
    ax1.set_xticklabels(data.index, rotation=30, ha='right', fontsize=10)
    ax1.set_xlabel('Nguồn truy cập (Traffic Source)', labelpad=8)
    ax1.set_ylabel('Số đơn hàng', color=VIBRANT[1], labelpad=8)
    ax2.set_ylabel('Tỷ lệ chuyển đổi (%)', color=VIBRANT[0], labelpad=8)
    
    ax1.tick_params(axis='y', colors=VIBRANT[1])
    ax2.tick_params(axis='y', colors=VIBRANT[0])

    # Legend
    h1 = [Patch(facecolor=VIBRANT[1], alpha=0.85, label='Số đơn hàng')]
    h2 = [Line2D([0], [0], color=VIBRANT[0], marker='D', linewidth=2, label='Tỷ lệ CV (%)')]
    fig.legend(handles=h1 + h2,
               loc='upper center', bbox_to_anchor=(0.5, 1.02),
               ncol=2, frameon=True, shadow=True, fontsize=11)

    apply_chart_title(ax1, 'Số đơn hàng và tỷ lệ chuyển đổi theo nguồn', pad=30)
    
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(os.path.join(CURRENT_DIR, '8_Orders_and_CVRate_by_Traffic_Source.png'),
                dpi=300, bbox_inches='tight')
    plt.close(fig)
def draw_chart_9(df_t):
    print("-> 9: Pageviews by Source...")
    data = df_t.groupby('traffic_source')['page_views'].sum().sort_values(ascending=False)
    n    = len(data)
    bar_colors = [VIBRANT[i % len(VIBRANT)] for i in range(n)]

    fig, ax = plt.subplots(figsize=(max(12, n * 1.5), 7))
    bars = ax.bar(range(n), data.values, color=bar_colors,
                  width=0.6, edgecolor='white', linewidth=1.5, alpha=0.9)

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(vn_format))
    for bar, val in zip(bars, data.values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + data.values.max() * 0.015,
                vn_format(val, None), ha='center', va='bottom',
                fontsize=9, fontweight='bold', color=TITLE_COLOR)

    ax.set_xticks(range(n))
    ax.set_xticklabels(data.index, rotation=30, ha='right', fontsize=10)
    ax.set_xlabel('Nguồn truy cập (Traffic Source)', labelpad=8)
    ax.set_ylabel('Tổng lượt xem trang (Pageviews)', labelpad=8)
    apply_chart_title(ax, 'Tổng pageviews theo nguồn truy cập', pad=20)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(CURRENT_DIR, '9_Pageviews_by_Traffic_Source.png'),
                dpi=300, bbox_inches='tight')
    plt.close(fig)


def draw_chart_10(df_m):
    print("-> 10: Doanh thu theo nhóm tuổi...")
    data = df_m.groupby('age_group')['order_revenue'].sum().sort_index()
    n    = len(data)
    bar_colors = [VIBRANT[i % len(VIBRANT)] for i in range(n)]

    fig, ax = plt.subplots(figsize=(max(12, n * 1.5), 7))
    bars = ax.bar(range(n), data.values, color=bar_colors,
                  width=0.6, edgecolor='white', linewidth=1.5, alpha=0.9)

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(vn_format))
    for bar, val in zip(bars, data.values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + data.values.max() * 0.015,
                vn_format(val, None), ha='center', va='bottom',
                fontsize=9, fontweight='bold', color=TITLE_COLOR)

    ax.set_xticks(range(n))
    ax.set_xticklabels(data.index, rotation=30, ha='right', fontsize=10)
    ax.set_xlabel('Nhóm tuổi (Age Group)', labelpad=8)
    ax.set_ylabel('Tổng doanh thu (VND)', labelpad=8)
    apply_chart_title(ax, 'Tổng doanh thu theo nhóm tuổi (VND)', pad=20)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(CURRENT_DIR, '10_Total_Revenue_by_Age_Group.png'),
                dpi=300, bbox_inches='tight')
    plt.close(fig)


def draw_chart_11(df_m):
    print("-> 11: Pareto Doanh thu theo Tuổi...")
    data = (df_m.groupby('age_group')['order_revenue']
            .sum().sort_values(ascending=False).reset_index())
    data['cum'] = (data['order_revenue'].cumsum() / data['order_revenue'].sum()) * 100
    n = len(data)

    fig, ax1 = plt.subplots(figsize=(max(13, n * 1.6), 8))
    grad_colors = plt.cm.Blues(np.linspace(0.4, 0.85, n))
    bars = ax1.bar(range(n), data['order_revenue'], color=grad_colors,
                   width=0.65, edgecolor='white', linewidth=1.5, alpha=0.9,
                   label='Doanh thu (VND)')

    for bar, val in zip(bars, data['order_revenue']):
        ax1.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + data['order_revenue'].max() * 0.015,
                 vn_format(val, None), ha='center', va='bottom',
                 fontsize=9, fontweight='bold', color=TITLE_COLOR)

    ax2 = ax1.twinx()
    ax2.plot(range(n), data['cum'].values, color=VIBRANT[0],
             marker='D', markersize=8, linewidth=2.5,
             markerfacecolor=VIBRANT[0], markeredgecolor='white', markeredgewidth=1.5,
             label='Tích lũy (%)', zorder=5)
    ax2.axhline(80, color='#F44336', linestyle='--', linewidth=2, zorder=4)
    ax2.text(n - 0.5, 81.5, 'Ngưỡng 80%',
             color='#F44336', fontsize=10, fontweight='bold', ha='right')

    setup_pretty_dual_axes(ax1, ax2, data['order_revenue'].max(), 100,
                           y1_formatter=vn_format, y2_formatter=percent_format,
                           keep_max2=True)
    ax1.set_xticks(range(n))
    ax1.set_xticklabels(data['age_group'], rotation=30, ha='right', fontsize=10)
    ax1.set_xlabel('Nhóm tuổi (Age Group)', labelpad=8)
    ax1.set_ylabel('Tổng doanh thu (VND)', color=VIBRANT[7], labelpad=8)
    ax2.set_ylabel('Tỷ lệ tích lũy (%)', color=VIBRANT[0], labelpad=8)
    ax1.tick_params(axis='y', colors=VIBRANT[7])
    ax2.tick_params(axis='y', colors=VIBRANT[0])

    h1 = [Patch(facecolor='#5C85D6', alpha=0.85, label='Doanh thu (VND)')]
    h2 = [Line2D([0], [0], color=VIBRANT[0], marker='D', linewidth=2, label='Tích lũy (%)')]
    h3 = [Line2D([0], [0], color='#F44336', linestyle='--', linewidth=2, label='Ngưỡng 80%')]
    fig.legend(handles=h1 + h2 + h3,
               loc='upper center', bbox_to_anchor=(0.5, 1.02),
               ncol=3, frameon=True, shadow=True, fontsize=11)

    apply_chart_title(ax1, 'Phân tích Pareto doanh thu theo nhóm tuổi', pad=30)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(os.path.join(CURRENT_DIR, '11_Pareto_Chart_Revenue_by_Age_Group.png'),
                dpi=300, bbox_inches='tight')
    plt.close(fig)


def draw_chart_12(df_m):
    print("-> 12: Đơn theo Phương thức thanh toán...")
    data = df_m.groupby('payment_method')['order_id'].nunique().sort_values(ascending=False)
    n    = len(data)
    bar_colors = [VIBRANT[i % len(VIBRANT)] for i in range(n)]

    fig, ax = plt.subplots(figsize=(max(12, n * 1.5), 7))
    bars = ax.bar(range(n), data.values, color=bar_colors,
                  width=0.6, edgecolor='white', linewidth=1.5, alpha=0.9)

    for bar, val in zip(bars, data.values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + data.values.max() * 0.015,
                f'{val:,.0f}', ha='center', va='bottom',
                fontsize=10, fontweight='bold', color=TITLE_COLOR)

    ax.set_xticks(range(n))
    ax.set_xticklabels(data.index, rotation=30, ha='right', fontsize=10)
    ax.set_xlabel('Phương thức thanh toán (Payment Method)', labelpad=8)
    ax.set_ylabel('Số lượng đơn hàng', labelpad=8)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    apply_chart_title(ax, 'Số lượng đơn hàng theo phương thức thanh toán', pad=20)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(CURRENT_DIR, '12_Orders_by_Payment_Method.png'),
                dpi=300, bbox_inches='tight')
    plt.close(fig)


def draw_chart_13(df_m):
    print("-> 13: AOV theo Kỳ trả góp...")
    valid = [1, 2, 3, 6, 12]
    d     = df_m[df_m['installments'].isin(valid)].groupby('installments')['order_revenue'].mean()
    n     = len(d)
    bar_colors = [VIBRANT[i % len(VIBRANT)] for i in range(n)]

    fig, ax = plt.subplots(figsize=(10, 7))
    bars = ax.bar(range(n), d.values, color=bar_colors,
                  width=0.55, edgecolor='white', linewidth=1.5, alpha=0.9)

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(vn_format))
    for bar, val in zip(bars, d.values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + d.values.max() * 0.015,
                vn_format(val, None), ha='center', va='bottom',
                fontsize=10, fontweight='bold', color=TITLE_COLOR)

    ax.set_xticks(range(n))
    ax.set_xticklabels([f'{k} kỳ' for k in d.index], fontsize=11)
    ax.set_xlabel('Số kỳ trả góp (Installments)', labelpad=8)
    ax.set_ylabel('Giá trị đơn hàng trung bình – AOV (VND)', labelpad=8)
    apply_chart_title(ax, 'AOV trung bình theo số kỳ trả góp (VND)', pad=20)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(CURRENT_DIR, '13_AOV_by_Number_of_Installments.png'),
                dpi=300, bbox_inches='tight')
    plt.close(fig)


# =====================================================================
# 6. CHƯƠNG TRÌNH CHÍNH
# =====================================================================
def main():
    print("--- BẮT ĐẦU MASTER DASHBOARD (VIBRANT EDITION) ---")
    try:
        df_m = pd.read_csv(PATH_MASTER, low_memory=False)
        df_m['order_date'] = pd.to_datetime(df_m['order_date'])
        df_t = pd.read_csv(PATH_TRAFFIC, low_memory=False)
        df_t['date'] = pd.to_datetime(df_t['date'])

        df_m['order_source']       = df_m['order_source'].str.lower().str.strip()
        df_t['traffic_source']     = df_t['traffic_source'].str.lower().str.strip()

        draw_chart_1(df_m, df_t);  draw_chart_2(df_m, df_t);  draw_chart_3(df_m, df_t)
        draw_chart_4(df_m);        draw_chart_5(df_m, df_t);  draw_chart_6(df_t)
        draw_chart_7(df_m, df_t);  draw_chart_8(df_m, df_t);  draw_chart_9(df_t)
        draw_chart_10(df_m);       draw_chart_11(df_m);        draw_chart_12(df_m)
        draw_chart_13(df_m)

        print("\n" + "="*55)
        print("✅ HOÀN TẤT! 13 BIỂU ĐỒ VIBRANT EDITION ĐÃ XUẤT.")
        print("="*55)
    except Exception as e:
        import traceback
        print(f"❌ LỖI: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()