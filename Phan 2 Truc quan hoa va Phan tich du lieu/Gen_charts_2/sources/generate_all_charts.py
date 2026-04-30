# -*- coding: utf-8 -*-
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

# Load data
print("Loading data...")
orders = pd.read_csv('data/orders.csv')
inventory = pd.read_csv('data/inventory.csv')
geography = pd.read_csv('data/geography.csv')
returns = pd.read_csv('data/returns.csv')
shipments = pd.read_csv('data/shipments.csv')
reviews = pd.read_csv('data/reviews.csv')
order_items = pd.read_csv('data/order_items.csv')
products = pd.read_csv('data/products.csv')
customers = pd.read_csv('data/customers.csv')
sales = pd.read_csv('data/sales.csv')

# Convert date columns
orders['order_date'] = pd.to_datetime(orders['order_date'])
customers['signup_date'] = pd.to_datetime(customers['signup_date'])
returns['return_date'] = pd.to_datetime(returns['return_date'])
shipments['delivery_date'] = pd.to_datetime(shipments['delivery_date'])
reviews['review_date'] = pd.to_datetime(reviews['review_date'])
inventory['snapshot_date'] = pd.to_datetime(inventory['snapshot_date'])
sales['Date'] = pd.to_datetime(sales['Date'])

print("Data loaded successfully!")

# ============ CHART 4.1: Stock Out Ratio by Month (120 months) ============
print("Creating Chart 4.1: Stock Out Ratio by Month...")
inventory['year_month'] = inventory['snapshot_date'].dt.to_period('M')
monthly_stock = inventory.groupby('year_month').apply(
    lambda x: (x['stockout_flag'].sum() / len(x)) * 100
).reset_index(name='stock_out_ratio')
monthly_stock['year_month'] = monthly_stock['year_month'].astype(str)

fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(range(len(monthly_stock)), monthly_stock['stock_out_ratio'], 
        linewidth=2, marker='o', markersize=4, color='#8B3A62')
ax.set_xlabel('Tháng (Month)', fontsize=12, fontweight='bold')
ax.set_ylabel('Stock Out Ratio (%)', fontsize=12, fontweight='bold')
ax.set_title('BIỂU ĐỒ 4.1: XU HƯỚNG STOCK OUT RATIO THEO THÁNG', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)
plt.xticks(range(0, len(monthly_stock), 12), [f"Month {i}" for i in range(0, len(monthly_stock), 12)], rotation=45)
plt.tight_layout()
plt.savefig('chart_4_1_stock_out_ratio.png', dpi=300, bbox_inches='tight')
plt.close()

# ============ CHART 2: Revenue and Stock Out Ratio Dual-Axis ============
print("Creating Chart 2: Revenue and Stock Out Ratio...")
sales['year_month'] = sales['Date'].dt.to_period('M')
monthly_revenue = sales.groupby('year_month')['Revenue'].sum().reset_index()
monthly_revenue['year_month'] = monthly_revenue['year_month'].astype(str)

# Merge with stock out ratio
monthly_combined = monthly_stock.copy()
monthly_combined.columns = ['year_month', 'stock_out_ratio']
monthly_combined['revenue'] = monthly_revenue['Revenue'].values

fig, ax1 = plt.subplots(figsize=(14, 6))
color = '#8B3A62'
ax1.set_xlabel('Tháng (Month)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Tổng Doanh Thu', color=color, fontsize=12, fontweight='bold')
line1 = ax1.plot(range(len(monthly_combined)), monthly_combined['revenue']/1e6, 
                 color=color, marker='o', linewidth=2, label='Tổng Doanh Thu')
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_ylim(bottom=0)  # Set Y-axis to start from 0
ax1.grid(True, alpha=0.3, linestyle='-', linewidth=0.8)  # Add grid

ax2 = ax1.twinx()
color = '#C85BA3'
ax2.set_ylabel('Stock Out Ratio (%)', color=color, fontsize=12, fontweight='bold')
line2 = ax2.plot(range(len(monthly_combined)), monthly_combined['stock_out_ratio'], 
                 color=color, marker='s', linewidth=2, label='Stock Out Ratio (%)  —  Đường thể hiện tỷ lệ hết hàng')
ax2.tick_params(axis='y', labelcolor=color)
ax2.set_ylim(bottom=0)  # Set Y-axis to start from 0

# Each axis has its own independent gridlines based on its actual values
# Left axis (Revenue): 0 to ~271.7, intervals of ~54.3
max_revenue = monthly_combined['revenue'].max() / 1e6
ax1.set_ylim(0, max_revenue * 1.05)
ax1.set_yticks(np.arange(0, max_revenue * 1.1, 54.3))
ax1.grid(True, alpha=0.3, linestyle='-', linewidth=0.8, axis='y')
ax1.set_axisbelow(True)

# Right axis (Stock Out Ratio): 0 to ~72.54%, intervals of ~14.51%
max_stockout = monthly_combined['stock_out_ratio'].max()
ax2.set_ylim(0, max_stockout * 1.05)
ax2.set_yticks(np.arange(0, max_stockout * 1.1, 14.51))

# Create combined legend positioned outside plot area
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
fig.legend(lines1 + lines2, labels1 + labels2, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2, fontsize=10, frameon=True)

fig.suptitle('Xu Hướng Doanh Thu và Stock Out Ratio', fontsize=14, fontweight='bold')
plt.xticks(range(0, len(monthly_combined), 12), [f"Month {i}" for i in range(0, len(monthly_combined), 12)], rotation=45)
fig.tight_layout()
plt.subplots_adjust(bottom=0.15)  # Add space for legend
plt.savefig('chart2_revenue_stockout.png', dpi=300, bbox_inches='tight')
plt.close()

# ============ CHART 4.2: Average Order Value by Region ============
print("Creating Chart 4.2: Average Order Value by Region...")
order_items['revenue'] = order_items['quantity'] * order_items['unit_price'] - order_items['discount_amount']
order_region = orders.merge(order_items, on='order_id').merge(geography, on='zip')
avg_order_by_region = order_region.groupby('region')['revenue'].mean().reset_index()
avg_order_by_region.columns = ['region', 'avg_order_value']
avg_order_by_region = avg_order_by_region.sort_values('avg_order_value', ascending=False)

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(avg_order_by_region['region'], avg_order_by_region['avg_order_value']/1e3, 
              color='#8B3A62', edgecolor='black', linewidth=1.5)
ax.set_xlabel('Vùng (Region)', fontsize=12, fontweight='bold')
ax.set_ylabel('Giá Trị Trung Bình Đơn (x1000)', fontsize=12, fontweight='bold')
ax.set_title('BIỂU ĐỒ 4.2: GIÁ TRỊ TRUNG BÌNH ĐƠN HÀNG THEO VÙNG', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('chart_4_2_avg_order_by_region.png', dpi=300, bbox_inches='tight')
plt.close()

# ============ CHART 4: Total Revenue by Region ============
print("Creating Chart 4: Total Revenue by Region...")
total_revenue_by_region = order_region.groupby('region')['revenue'].sum().reset_index()
total_revenue_by_region.columns = ['region', 'total_revenue']
total_revenue_by_region = total_revenue_by_region.sort_values('total_revenue', ascending=False)

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(total_revenue_by_region['region'], total_revenue_by_region['total_revenue']/1e9, 
              color='#A85282', edgecolor='black', linewidth=1.5)
ax.set_xlabel('Vùng (Region)', fontsize=12, fontweight='bold')
ax.set_ylabel('Tổng Doanh Thu (Tỷ)', fontsize=12, fontweight='bold')
ax.set_title('Tổng Doanh Thu Theo Vùng', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('chart4_revenue_by_region.png', dpi=300, bbox_inches='tight')
plt.close()

# ============ CHART 5: Orders by Category and Segment ============
print("Creating Chart 5: Orders by Category and Segment...")
order_product = order_items.merge(products, on='product_id')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# By Category
orders_by_category = order_product.groupby('category').size().reset_index(name='order_count')
orders_by_category = orders_by_category.sort_values('order_count', ascending=False)
ax1.bar(orders_by_category['category'], orders_by_category['order_count'], 
        color='#8B3A62', edgecolor='black', linewidth=1.5)
ax1.set_xlabel('Danh Mục (Category)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Số Đơn Đặt Hàng', fontsize=12, fontweight='bold')
ax1.set_title('Số Lượng Đơn Hàng Theo Danh Mục', fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3, axis='y')
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

# By Segment
orders_by_segment = order_product.groupby('segment').size().reset_index(name='order_count')
orders_by_segment = orders_by_segment.sort_values('order_count', ascending=False)
ax2.bar(orders_by_segment['segment'], orders_by_segment['order_count'], 
        color='#C85BA3', edgecolor='black', linewidth=1.5)
ax2.set_xlabel('Phân Khúc (Segment)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Số Đơn Đặt Hàng', fontsize=12, fontweight='bold')
ax2.set_title('Số Lượng Đơn Hàng Theo Phân Khúc Sản Phẩm', fontsize=13, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='y')
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.savefig('chart5_orders_category_segment.png', dpi=300, bbox_inches='tight')
plt.close()

# ============ CHART 6: Return Reasons Trend Over Years ============
print("Creating Chart 6: Return Reasons Trend...")
returns_orders = returns.merge(orders[['order_id', 'order_date']], on='order_id')
returns_orders['year'] = returns_orders['return_date'].dt.year
reason_trend = returns_orders.groupby(['year', 'return_reason']).size().reset_index(name='count')

fig, ax = plt.subplots(figsize=(14, 7))
for reason in reason_trend['return_reason'].unique():
    data = reason_trend[reason_trend['return_reason'] == reason]
    ax.plot(data['year'], data['count'], marker='o', linewidth=2, label=reason)

ax.set_xlabel('Năm (Year)', fontsize=12, fontweight='bold')
ax.set_ylabel('Số Lượng Đơn Hàng Trả Lại', fontsize=12, fontweight='bold')
ax.set_title('Xu Hướng Lý Do Trả Lại Hàng Qua Các Năm', fontsize=14, fontweight='bold')
ax.legend(loc='best', fontsize=10)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('chart6_return_reasons_trend.png', dpi=300, bbox_inches='tight')
plt.close()

# ============ CHART 7: Returned Orders by Year ============
print("Creating Chart 7: Returned Orders by Year...")
returns_orders['order_year'] = returns_orders['order_date'].dt.year
returns_by_year = returns_orders.groupby('order_year').size().reset_index(name='return_count')

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(returns_by_year['order_year'], returns_by_year['return_count'], 
              color='#C85BA3', edgecolor='black', linewidth=1.5)
ax.set_xlabel('Năm (Year)', fontsize=12, fontweight='bold')
ax.set_ylabel('Số Lượng Đơn Hàng Trả Lại', fontsize=12, fontweight='bold')
ax.set_title('Số Lượng Đơn Hàng Trả Lại Theo Năm', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')
plt.xticks(returns_by_year['order_year'])
plt.tight_layout()
plt.savefig('chart7_returns_by_year.png', dpi=300, bbox_inches='tight')
plt.close()

# ============ CHART 8: Orders by Rating Score ============
print("Creating Chart 8: Orders by Rating Score...")
rating_counts = reviews.groupby('rating').size().reset_index(name='order_count')
rating_counts = rating_counts.sort_values('rating')

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(rating_counts['rating'], rating_counts['order_count'], 
              color='#A85282', edgecolor='black', linewidth=1.5)
ax.set_xlabel('Mức Điểm Đánh Giá (Rating)', fontsize=12, fontweight='bold')
ax.set_ylabel('Số Lượng Đơn Hàng', fontsize=12, fontweight='bold')
ax.set_title('Số Lượng Đơn Hàng Đánh Giá Theo Mức Điểm', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')
plt.xticks(rating_counts['rating'])
plt.tight_layout()
plt.savefig('chart8_orders_by_rating.png', dpi=300, bbox_inches='tight')
plt.close()

# ============ CHART 9: Average Lead Time by Region ============
print("Creating Chart 9: Average Lead Time by Region...")
shipment_orders = orders.merge(shipments, on='order_id').merge(geography, on='zip')
shipment_orders['lead_time'] = (shipment_orders['delivery_date'] - shipment_orders['order_date']).dt.days
avg_lead_time = shipment_orders.groupby('region')['lead_time'].mean().reset_index()
avg_lead_time.columns = ['region', 'avg_lead_time']
avg_lead_time = avg_lead_time.sort_values('avg_lead_time', ascending=False)

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(avg_lead_time['region'], avg_lead_time['avg_lead_time'], 
              color='#6B2A4A', edgecolor='black', linewidth=1.5)
ax.set_xlabel('Vùng (Region)', fontsize=12, fontweight='bold')
ax.set_ylabel('Thời Gian Giao Hàng Trung Bình (Ngày)', fontsize=12, fontweight='bold')
ax.set_title('Average Lead Time by Region', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('chart9_avg_lead_time_by_region.png', dpi=300, bbox_inches='tight')
plt.close()

# ============ CHART 2.2 & 3.1: Average Time Between Consecutive Purchases ============
print("Creating Chart 2.2 & 3.1: Average Time Between Consecutive Purchases...")
customer_orders = orders.sort_values(['customer_id', 'order_date']).reset_index(drop=True)
customer_orders['purchase_order'] = customer_orders.groupby('customer_id').cumcount() + 1

purchase_intervals = []
for customer_id in customer_orders['customer_id'].unique():
    cust_data = customer_orders[customer_orders['customer_id'] == customer_id].sort_values('order_date')
    if len(cust_data) > 1:
        dates = cust_data['order_date'].values
        for i in range(len(dates) - 1):
            interval = (dates[i+1] - dates[i]) / np.timedelta64(1, 'D')
            purchase_intervals.append({
                'from_purchase': i + 1,
                'to_purchase': i + 2,
                'interval_days': interval
            })

purchase_intervals_df = pd.DataFrame(purchase_intervals)
avg_intervals = purchase_intervals_df.groupby('from_purchase')['interval_days'].mean().reset_index()
avg_intervals.columns = ['purchase_order', 'avg_days']
avg_intervals['purchase_label'] = 'Order ' + avg_intervals['purchase_order'].astype(str) + '-' + (avg_intervals['purchase_order']+1).astype(str)

# Version 2.2
fig, ax = plt.subplots(figsize=(14, 6))
bars = ax.bar(range(len(avg_intervals)), avg_intervals['avg_days'], 
              color='#A85282', alpha=0.7, label='Số Ngày TB')
ax.plot(range(len(avg_intervals)), avg_intervals['avg_days'], 
         color='#8B3A62', linewidth=1.5, markersize=6, label='Xu Hướng', zorder=3)
ax.set_xlabel('Khoảng Cách Giữa Các Lần Mua', fontsize=12, fontweight='bold')
ax.set_ylabel('Số Ngày Trung Bình', fontsize=12, fontweight='bold')
ax.set_title('BIỂU ĐỒ 2.2: KHOẢNG THỜI GIAN TRUNG BÌNH GIỮA CÁC LẦN MUA LIÊN TIẾP', fontsize=14, fontweight='bold')
ax.set_ylim(bottom=0)
ax.grid(True, alpha=0.3, axis='y', linestyle='-', linewidth=0.8)
ax.legend(fontsize=11, loc='best')
plt.xticks(range(0, len(avg_intervals), max(1, len(avg_intervals)//10)), 
           [avg_intervals['purchase_label'].iloc[i] if i < len(avg_intervals) else '' 
            for i in range(0, len(avg_intervals), max(1, len(avg_intervals)//10))], rotation=45, ha='right')
plt.tight_layout()
plt.savefig('chart_2_2_purchase_intervals.png', dpi=300, bbox_inches='tight')
plt.close()

# Version 3.1
fig, ax = plt.subplots(figsize=(14, 6))
bars = ax.bar(range(len(avg_intervals)), avg_intervals['avg_days'], 
              color='#A85282', alpha=0.7, label='Số Ngày TB')
ax.plot(range(len(avg_intervals)), avg_intervals['avg_days'], 
         color='#8B3A62', linewidth=1.5, markersize=6, label='Xu Hướng', zorder=3)
ax.set_xlabel('Khoảng Cách Giữa Các Lần Mua', fontsize=12, fontweight='bold')
ax.set_ylabel('Số Ngày Trung Bình', fontsize=12, fontweight='bold')
ax.set_title('BIỂU ĐỒ 3.1: KHOẢNG THỜI GIAN TRUNG BÌNH GIỮA CÁC LẦN MUA LIÊN TIẾP', fontsize=14, fontweight='bold')
ax.set_ylim(bottom=0)
ax.grid(True, alpha=0.3, axis='y', linestyle='-', linewidth=0.8)
ax.legend(fontsize=11, loc='best')
plt.xticks(range(0, len(avg_intervals), max(1, len(avg_intervals)//10)), 
           [avg_intervals['purchase_label'].iloc[i] if i < len(avg_intervals) else '' 
            for i in range(0, len(avg_intervals), max(1, len(avg_intervals)//10))], rotation=45, ha='right')
plt.tight_layout()
plt.savefig('chart_3_1_purchase_intervals.png', dpi=300, bbox_inches='tight')
plt.close()

# ============ CHART 3.2: Average Order Value by Full Purchase Sequence ============
print("Creating Chart 3.2: Average Order Value by Purchase Sequence...")
customer_order_revenue = orders.merge(order_items, on='order_id').merge(customers[['customer_id']], on='customer_id')
customer_order_revenue['revenue'] = customer_order_revenue['quantity'] * customer_order_revenue['unit_price'] - customer_order_revenue['discount_amount']
customer_order_revenue = customer_order_revenue.sort_values(['customer_id', 'order_date']).reset_index(drop=True)
customer_order_revenue['purchase_order'] = customer_order_revenue.groupby('customer_id').cumcount() + 1

avg_revenue_by_order = customer_order_revenue.groupby('purchase_order')['revenue'].mean().reset_index()
avg_revenue_by_order.columns = ['order_number', 'avg_revenue']

fig, ax = plt.subplots(figsize=(14, 6))

# Bar chart
bars = ax.bar(range(len(avg_revenue_by_order)), avg_revenue_by_order['avg_revenue']/1e3, 
              color='#A85282', alpha=0.7, label='Giá Trị Trung Bình (x1000)')

# Line trend
ax.plot(range(len(avg_revenue_by_order)), avg_revenue_by_order['avg_revenue']/1e3, 
         color='#8B3A62', linewidth=1.5, markersize=6, label='Xu Hướng', zorder=3)

ax.set_xlabel('Số Lần Mua (Order Number)', fontsize=12, fontweight='bold')
ax.set_ylabel('Giá Trị Đơn Hàng Trung Bình (x1000)', fontsize=12, fontweight='bold')
ax.set_title('BIỂU ĐỒ 3.2: GIÁ TRỊ ĐƠN HÀNG TRUNG BÌNH THEO LẦN MUA LIÊN TIẾP', fontsize=14, fontweight='bold')
ax.set_ylim(bottom=0)  # Ensure 0 is at the bottom
ax.grid(True, alpha=0.3, axis='y', linestyle='-', linewidth=0.8)  # Overlapping grids
ax.legend(fontsize=11, loc='best')
# Set equal spacing between x-ticks
ax.set_xticks(range(0, len(avg_revenue_by_order), max(1, len(avg_revenue_by_order)//15)))
ax.set_xticklabels([str(i+1) if i < len(avg_revenue_by_order) else '' 
                     for i in range(0, len(avg_revenue_by_order), max(1, len(avg_revenue_by_order)//15))], rotation=45)
plt.tight_layout()
plt.savefig('chart_3_2_avg_order_value_sequence.png', dpi=300, bbox_inches='tight')
plt.close()

# ============ CHART 12: New Customers by Year with Trend ============
print("Creating Chart 12: New Customers by Year (Based on First Order)...")
# CORRECTED LOGIC: New customer = customer who placed their FIRST order in a specific year
df_first_purchase = orders.groupby('customer_id')['order_date'].min().reset_index()
df_first_purchase.columns = ['customer_id', 'first_order_date']
df_first_purchase['first_order_year'] = df_first_purchase['first_order_date'].dt.year

# Count new customers by their first order year
new_customers = df_first_purchase.groupby('first_order_year').size().reset_index(name='new_customer_count')
new_customers.columns = ['year', 'new_customer_count']

# Verification: Check count for 2012
unique_customers_2012 = new_customers[new_customers['year'] == 2012]['new_customer_count'].values
print(f"  [VERIFY] New customers (first order) in 2012: {unique_customers_2012[0] if len(unique_customers_2012) > 0 else 'N/A'}")

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(new_customers['year'], new_customers['new_customer_count'], 
              color='#8B3A62', alpha=0.7, edgecolor='black', linewidth=1.5)

# Add trend line
z = np.polyfit(new_customers['year'], new_customers['new_customer_count'], 2)
p = np.poly1d(z)
ax.plot(new_customers['year'], p(new_customers['year']), 
        "r-", linewidth=2.5, label='Xu Hướng')

ax.set_xlabel('Năm (Year)', fontsize=12, fontweight='bold')
ax.set_ylabel('Số Lượng Khách Hàng Mới', fontsize=12, fontweight='bold')
ax.set_title('Số Lượng Khách Hàng Mới (Mua Lần Đầu) Theo Năm', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')
ax.legend()
plt.xticks(new_customers['year'])
plt.tight_layout()
plt.savefig('chart12_new_customers_by_year.png', dpi=300, bbox_inches='tight')
plt.close()

# ============ CHART 13: Returning Customers by Year with Trend ============
print("Creating Chart 13: Returning Customers by Year (Based on First Order)...")
# CORRECTED LOGIC: Returning customer = customer whose order year > their first order year
orders['order_year'] = orders['order_date'].dt.year

# Merge orders with first purchase info
orders_with_first = orders.merge(df_first_purchase[['customer_id', 'first_order_year']], on='customer_id')

# Filter for returning customers (order_year > first_order_year) and year range 2013-2022
returning = orders_with_first[(orders_with_first['order_year'] > orders_with_first['first_order_year']) & 
                               (orders_with_first['order_year'] >= 2013) & 
                               (orders_with_first['order_year'] <= 2022)]
returning_by_year = returning.groupby('order_year')['customer_id'].nunique().reset_index(name='returning_customer_count')
returning_by_year.columns = ['year', 'returning_customer_count']

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(returning_by_year['year'], returning_by_year['returning_customer_count'], 
              color='#A85282', alpha=0.7, edgecolor='black', linewidth=1.5)

# Add trend line
z = np.polyfit(returning_by_year['year'], returning_by_year['returning_customer_count'], 2)
p = np.poly1d(z)
ax.plot(returning_by_year['year'], p(returning_by_year['year']), 
        "b-", linewidth=2.5, label='Xu Hướng')

ax.set_xlabel('Năm (Year)', fontsize=12, fontweight='bold')
ax.set_ylabel('Số Lượng Khách Hàng Quay Lại', fontsize=12, fontweight='bold')
ax.set_title('Số Lượng Khách Hàng Quay Lại Theo Năm (2013-2022)', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')
ax.legend()
plt.xticks(range(2013, 2023))
plt.tight_layout()
plt.savefig('chart13_returning_customers_by_year.png', dpi=300, bbox_inches='tight')
plt.close()

# ============ CHART 3.3: New vs Returning Customers Trend (2013-2022) ============
print("Creating Chart 3.3: New vs Returning Customers Trend (Based on First Order)...")

# Filter new customers for 2013-2022
new_by_year = new_customers[(new_customers['year'] >= 2013) & (new_customers['year'] <= 2022)].copy()

# Filter returning customers for 2013-2022
returning_filtered = returning_by_year[(returning_by_year['year'] >= 2013) & (returning_by_year['year'] <= 2022)].copy()

# Merge to ensure alignment and calculate total
chart14_data = new_by_year.merge(returning_filtered, on='year', how='outer').fillna(0)
chart14_data['new_customer_count'] = chart14_data['new_customer_count'].astype(int)
chart14_data['returning_customer_count'] = chart14_data['returning_customer_count'].astype(int)
chart14_data['total_count'] = chart14_data['new_customer_count'] + chart14_data['returning_customer_count']

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(chart14_data['year'], chart14_data['new_customer_count'], 
        marker='o', linewidth=2.5, markersize=8, label='Khách Hàng Mới', color='#8B3A62')
ax.plot(chart14_data['year'], chart14_data['returning_customer_count'], 
        marker='s', linewidth=2.5, markersize=8, label='Khách Hàng Quay Lại', color='#A85282')
ax.plot(chart14_data['year'], chart14_data['total_count'], 
        marker='^', linewidth=2.5, markersize=8, label='Tổng Cộng', color='#C85BA3', linestyle='--')

ax.set_xlabel('Năm (Year)', fontsize=12, fontweight='bold')
ax.set_ylabel('Số Lượng Khách Hàng', fontsize=12, fontweight='bold')
ax.set_title('BIỂU ĐỒ 3.3: XU HƯỚNG KHÁCH HÀNG MỚI VÀ QUAY LẠI (2013-2022)', fontsize=14, fontweight='bold')
ax.legend(fontsize=11, loc='best')
ax.grid(True, alpha=0.3)
plt.xticks(range(2013, 2023))
plt.tight_layout()
plt.savefig('chart_3_3_new_vs_returning_customers.png', dpi=300, bbox_inches='tight')
plt.close()

print("\n" + "="*50)
print("✓ Tất cả biểu đồ đã được tạo thành công!")
print("="*50)
print("Các tệp PNG được tạo:")
print("1. chart1_stock_out_ratio.png")
print("2. chart2_revenue_stockout.png")
print("3. chart3_avg_order_by_region.png")
print("4. chart4_revenue_by_region.png")
print("5. chart5_orders_category_segment.png")
print("6. chart6_return_reasons_trend.png")
print("7. chart7_returns_by_year.png")
print("8. chart8_orders_by_rating.png")
print("9. chart9_avg_lead_time_by_region.png")
print("10. chart10_purchase_intervals.png")
print("11. chart11_avg_order_value_sequence.png")
print("12. chart12_new_customers_by_year.png")
print("13. chart13_returning_customers_by_year.png")
print("14. chart14_new_vs_returning_customers.png")
