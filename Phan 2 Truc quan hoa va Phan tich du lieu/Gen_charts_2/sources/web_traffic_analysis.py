import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load data
web_traffic = pd.read_csv('data/web_traffic.csv')
orders = pd.read_csv('data/orders.csv')
sales = pd.read_csv('data/sales.csv')

# Convert date columns to datetime
web_traffic['date'] = pd.to_datetime(web_traffic['date'])
orders['order_date'] = pd.to_datetime(orders['order_date'])
sales['Date'] = pd.to_datetime(sales['Date'])

# Extract year from dates
web_traffic['year'] = web_traffic['date'].dt.year
orders['year'] = orders['order_date'].dt.year
sales['year'] = sales['Date'].dt.year

# ===== Chart 1: Total Sessions by Year (Line Chart) =====
sessions_by_year = web_traffic.groupby('year')['sessions'].sum().reset_index()
sessions_by_year.columns = ['Năm', 'Tổng Sessions']

fig1 = px.line(
    sessions_by_year,
    x='Năm',
    y='Tổng Sessions',
    markers=True,
    title='BIỂU ĐỒ 2.3: TỔNG SỐ SESSIONS QUA CÁC NĂM (THEO NĂM)',
    labels={'Năm': 'Năm', 'Tổng Sessions': 'Tổng Sessions'},
    line_shape='linear',
    color_discrete_sequence=['#8B3A62']
)
fig1.update_traces(line=dict(color='#8B3A62', width=3), marker=dict(size=8))

fig1.update_xaxes(
    tickmode='linear',
    tick0=sessions_by_year['Năm'].min(),
    dtick=1
)

fig1.write_image('charts/sessions_by_year_line_chart.png', width=1200, height=600)
print("✓ Chart 1 (Sessions by Year) saved: charts/sessions_by_year_line_chart.png")

# ===== Chart 2: AOV by Year (Column Chart) =====
# Calculate total orders per year
orders_by_year = orders.groupby('year').size().reset_index(name='total_orders')

# Calculate total revenue per year
revenue_by_year = sales.groupby('year')['Revenue'].sum().reset_index()
revenue_by_year.columns = ['year', 'total_revenue']

# Merge the data
aov_data = pd.merge(revenue_by_year, orders_by_year, on='year')

# Calculate AOV
aov_data['AOV'] = aov_data['total_revenue'] / aov_data['total_orders']
aov_data['Năm'] = aov_data['year'].astype(int)
aov_data['Chỉ số AOV'] = aov_data['AOV'].round(2)

fig2 = px.bar(
    aov_data,
    x='Năm',
    y='Chỉ số AOV',
    title='BIỂU ĐỒ 2.4: CHỈ SỐ AOV (AVERAGE ORDER VALUE) THEO TỪNG NĂM',
    labels={'Năm': 'Năm', 'Chỉ số AOV': 'AOV (Doanh thu/Đơn hàng)'},
    text='Chỉ số AOV',
    color_discrete_sequence=['#8B3A62']
)
fig2.update_traces(marker=dict(color='#8B3A62'), textposition='outside')
fig2.update_xaxes(
    tickmode='linear',
    tick0=aov_data['year'].min(),
    dtick=1
)

fig2.write_image('charts/aov_by_year_column_chart.png', width=1200, height=600)
print("✓ Chart 2 (AOV by Year) saved: charts/aov_by_year_column_chart.png")

# Print summary statistics
print("\n" + "="*60)
print("THỐNG KÊ SESSIONS QUA CÁC NĂM")
print("="*60)
print(sessions_by_year.to_string(index=False))

print("\n" + "="*60)
print("THỐNG KÊ AOV QUA CÁC NĂM")
print("="*60)
print(aov_data[['Năm', 'total_revenue', 'total_orders', 'Chỉ số AOV']].to_string(index=False))
