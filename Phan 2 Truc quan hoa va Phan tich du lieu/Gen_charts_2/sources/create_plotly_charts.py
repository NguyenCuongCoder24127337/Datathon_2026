"""
🎨 PLOTLY VISUALIZATIONS - 3 Chìa Khóa Trao Tay
Doanh thu, Đơn hàng, và Phân tích Pareto
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("PLOTLY VISUALIZATIONS - 3 CHÍA KHOÁ TRAO TAY")
print("=" * 70)

# ============================================================================
# CHUẨN BỊ DỮ LIỆU
# ============================================================================
print("\nDang chuan bi du lieu...")

# Load dữ liệu
df_orders = pd.read_csv('data/orders.csv')
df_order_items = pd.read_csv('data/order_items.csv')
df_products = pd.read_csv('data/products.csv')

# Merge để lấy thông tin sản phẩm
df_merged = df_order_items.merge(df_products[['product_id', 'segment']], on='product_id')
df_merged = df_merged.merge(df_orders[['order_id', 'order_date']], on='order_id')

# Tính toán revenue (unit_price * quantity - discount_amount)
df_merged['revenue'] = (df_merged['unit_price'] * df_merged['quantity']) - df_merged['discount_amount']

# Chuyển đổi date
df_merged['order_date'] = pd.to_datetime(df_merged['order_date'])
df_merged['year'] = df_merged['order_date'].dt.year

print(f"+ Du lieu da duoc chuan bi!")
print(f"  - Tong dong: {len(df_merged):,.0f}")
print(f"  - Phan khuc: {df_merged['segment'].nunique()}")
print(f"  - Nam: {sorted(df_merged['year'].unique())}")

# ============================================================================
# PROMPT 1: LINE CHART - DOANH THU THEO NĂM & PHÂN KHÚC
# ============================================================================
print("\n" + "=" * 70)
print("PROMPT 1: LINE CHART - DOANH THU THEO NAM & PHAN KHUC")
print("=" * 70)

# Tập hợp dữ liệu theo năm và segment
df_by_year_segment = df_merged.groupby(['year', 'segment'])['revenue'].sum().reset_index()
df_by_year_segment.columns = ['year', 'product_segment', 'total_revenue']

# Tạo Line Chart với Plotly Express
fig1 = px.line(
    df_by_year_segment,
    x='year',
    y='total_revenue',
    color='product_segment',
    markers=True,
    title='Doanh thu theo Năm và Phân khúc sản phẩm',
    template='plotly_white',
    labels={'total_revenue': 'Doanh thu', 'year': 'Năm', 'product_segment': 'Phân khúc'},
    hover_data={'total_revenue': ':.2f'}
)

fig1.update_traces(marker=dict(size=8))
fig1.update_layout(
    hovermode='x unified',
    height=600,
    width=1000,
    font=dict(size=12),
    yaxis_title='Doanh thu (VND)',
    xaxis_title='Năm',
    legend=dict(
        orientation="v",
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ),
    plot_bgcolor='rgba(240, 240, 240, 0.5)',
    paper_bgcolor='white'
)
fig1.update_xaxes(showgrid=False)
fig1.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

# Lưu thành HTML và PNG
fig1.write_html('chart1_line_revenue_by_year_segment.html')
fig1.write_image('chart1_line_revenue_by_year_segment.png', width=1200, height=700)
print("+ Line Chart hoan thanh!")
print(f"  [FILE] Luu vao: chart1_line_revenue_by_year_segment.html")
print(f"  [IMAGE] Luu vao: chart1_line_revenue_by_year_segment.png")
print(f"  [DATA] Doanh thu tu {df_by_year_segment['year'].min()} den {df_by_year_segment['year'].max()}")

# ============================================================================
# PROMPT 2: COMBO CHART - DOANH THU & SỐ LƯỢNG ĐƠN
# ============================================================================
print("\n" + "=" * 70)
print("PROMPT 2: COMBO CHART - DOANH THU & SO LUONG DON")
print("=" * 70)

# Tập hợp dữ liệu theo segment
df_segment = df_merged.groupby('segment').agg({
    'revenue': 'sum',
    'order_id': 'nunique'
}).reset_index()
df_segment.columns = ['product_segment', 'total_revenue', 'order_count']

# Sắp xếp giảm dần theo revenue
df_segment = df_segment.sort_values('total_revenue', ascending=False)

# Tạo Combo Chart với Plotly Graph Objects
fig2 = make_subplots(
    rows=1, cols=1,
    specs=[[{'secondary_y': True}]]
)

# Thêm Bar chart cho revenue (trục Y trái)
fig2.add_trace(
    go.Bar(
        x=df_segment['product_segment'],
        y=df_segment['total_revenue'],
        name='Doanh thu',
        marker_color='steelblue',
        hovertemplate='<b>%{x}</b><br>Doanh thu: %{y:,.0f}<extra></extra>'
    ),
    secondary_y=False
)

# Thêm Line chart cho order_count (trục Y phải)
fig2.add_trace(
    go.Scatter(
        x=df_segment['product_segment'],
        y=df_segment['order_count'],
        name='Số lượng đơn',
        mode='lines+markers',
        line=dict(color='coral', width=3),
        marker=dict(size=10),
        hovertemplate='<b>%{x}</b><br>Số lượng đơn: %{y:,.0f}<extra></extra>'
    ),
    secondary_y=True
)

# Cập nhật layout
fig2.update_layout(
    title='Doanh thu & Số lượng đơn hàng theo Phân khúc',
    template='plotly_white',
    hovermode='x unified',
    height=600,
    width=1000,
    font=dict(size=12),
    legend=dict(x=0.5, y=1.08, orientation='h'),
    plot_bgcolor='rgba(240, 240, 240, 0.5)',
    paper_bgcolor='white'
)

# Đặt tên cho trục Y
fig2.update_yaxes(title_text='Doanh thu (VND)', secondary_y=False, showgrid=True, gridwidth=1, gridcolor='lightgray')
fig2.update_yaxes(title_text='Số lượng đơn', secondary_y=True, showgrid=False)
fig2.update_xaxes(title_text='Phân khúc sản phẩm', showgrid=False)

# Lưu thành HTML và PNG
fig2.write_html('chart2_combo_revenue_orders.html')
fig2.write_image('chart2_combo_revenue_orders.png', width=1200, height=700)
print("+ Combo Chart hoan thanh!")
print(f"  [FILE] Luu vao: chart2_combo_revenue_orders.html")
print(f"  [IMAGE] Luu vao: chart2_combo_revenue_orders.png")
print(f"  [DATA] {len(df_segment)} phan khuc duoc phan tich")

# ============================================================================
# PROMPT 3: PARETO CHART - QUY LUẬT 80/20
# ============================================================================
print("\n" + "=" * 70)
print("PROMPT 3: PARETO CHART - QUY LUAT 80/20")
print("=" * 70)

# Tập hợp dữ liệu theo segment
df_pareto = df_merged.groupby('segment')['revenue'].sum().reset_index()
df_pareto.columns = ['segment', 'total_revenue']

# Sắp xếp giảm dần
df_pareto = df_pareto.sort_values('total_revenue', ascending=False).reset_index(drop=True)

# Tính phần trăm tích lũy
total_revenue = df_pareto['total_revenue'].sum()
df_pareto['percentage'] = (df_pareto['total_revenue'] / total_revenue) * 100
df_pareto['cumulative_percentage'] = df_pareto['percentage'].cumsum()

# Tạo Pareto Chart
fig3 = make_subplots(
    rows=1, cols=1,
    specs=[[{'secondary_y': True}]]
)

# Thêm Bar chart cho revenue (trục Y trái)
fig3.add_trace(
    go.Bar(
        x=df_pareto['segment'],
        y=df_pareto['total_revenue'],
        name='Doanh thu',
        marker_color='lightblue',
        hovertemplate='<b>%{x}</b><br>Doanh thu: %{y:,.0f}<br>Tỷ lệ: %{customdata:.1f}%<extra></extra>',
        customdata=df_pareto['percentage']
    ),
    secondary_y=False
)

# Thêm Line chart cho cumulative percentage (trục Y phải)
fig3.add_trace(
    go.Scatter(
        x=df_pareto['segment'],
        y=df_pareto['cumulative_percentage'],
        name='% tích lũy',
        mode='lines+markers',
        line=dict(color='darkred', width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>% tích lũy: %{y:.1f}%<extra></extra>'
    ),
    secondary_y=True
)

# Thêm đường kẻ ngang tại 80% - CẮT PARETO (thêm vào legend)
fig3.add_hline(
    y=80,
    line_dash='dash',
    line_color='crimson',
    line_width=2,
    secondary_y=True
)

# Thêm trace ảo cho legend của điểm cắt Pareto
fig3.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode='lines',
        line=dict(color='crimson', width=2, dash='dash'),
        name='Điểm cắt Pareto (80%)',
        showlegend=True
    ),
    secondary_y=True
)

# Cập nhật layout
fig3.update_layout(
    title='Biểu đồ Pareto: Phân tích Doanh thu theo Phân khúc',
    template='plotly_white',
    hovermode='x unified',
    height=600,
    width=1000,
    font=dict(size=12),
    legend=dict(x=0.5, y=1.08, orientation='h'),
    showlegend=True,
    plot_bgcolor='rgba(240, 240, 240, 0.5)',
    paper_bgcolor='white'
)

# Đặt tên cho trục
fig3.update_yaxes(title_text='Doanh thu (VND)', secondary_y=False, showgrid=True, gridwidth=1, gridcolor='lightgray')
fig3.update_yaxes(title_text='Phần trăm tích lũy (%)', range=[0, 110], secondary_y=True, showgrid=False)
fig3.update_xaxes(title_text='Phân khúc sản phẩm', showgrid=False)

# Lưu thành HTML
fig3.write_html('chart3_pareto_80_20.html')
fig3.write_image('chart3_pareto_80_20.png', width=1200, height=700)
print("+ Pareto Chart hoan thanh!")
print(f"  [FILE] Luu vao: chart3_pareto_80_20.html")
print(f"  [IMAGE] Luu vao: chart3_pareto_80_20.png")

# ============================================================================
# INSIGHTS & PHÂN TÍCH
# ============================================================================
print("\n" + "=" * 70)
print("INSIGHTS & PHAN TICH")
print("=" * 70)

# Tìm segment nào chiếm 80% doanh thu
pareto_80 = df_pareto[df_pareto['cumulative_percentage'] <= 80]
count_80 = len(pareto_80)
total_segments = len(df_pareto)

print(f"\n[PARETO] Cac segment chiem 80% doanh thu (top {count_80}/{total_segments}):")
for idx, row in pareto_80.iterrows():
    print(f"   {idx+1}. {row['segment']:15} | Doanh thu: {row['total_revenue']:15,.0f} VND | % tich luy: {row['cumulative_percentage']:6.1f}%")

print(f"\n[CONCLUSION] Ket luan Pareto:")
print(f"   - {count_80} phan khuc ({count_80/total_segments*100:.1f}%) chiem {pareto_80['percentage'].sum():.1f}% doanh thu")
print(f"   - Nen tap trung vao {count_80} segment nay de toi da hoa ROI")
print(f"   - Co the giam nguon luc cho {total_segments - count_80} segment con lai")

# Xep hang theo doanh thu
print(f"\n[RANKING] Xep hang Phan khuc theo Doanh thu:")
for idx, row in df_segment.iterrows():
    percentage = (row['total_revenue'] / df_segment['total_revenue'].sum()) * 100
    bar_length = int(percentage / 2)
    bar = "=" * bar_length
    print(f"   {idx+1}. {row['product_segment']:15} | {bar:25} | {percentage:5.1f}% | {row['total_revenue']:15,.0f} VND")

print("\n" + "=" * 70)
print("[SUCCESS] TAT CA BIEU DO DA DUOC TAO VA LUU THANH CONG!")
print("=" * 70)
print("\n[FILES] Cac file HTML duoc tao:")
print("   1. chart1_line_revenue_by_year_segment.html - Doanh thu theo Nam & Phan khuc")
print("   2. chart2_combo_revenue_orders.html        - Doanh thu & So luong don")
print("   3. chart3_pareto_80_20.html                - Phan tich Pareto 80/20")
print("\n[BROWSER] Mo cac file .html trong trinh duyet de xem bieu do tuong tac!")
print("=" * 70)
