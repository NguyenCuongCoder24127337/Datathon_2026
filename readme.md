# DATATHON 2026 - THE GRIDBREAKER

**Cuộc thi**: Datathon 2026 (VinTelligence - VinUniversity)  
**Chủ đề**: Dự báo doanh thu cho công ty thương mại điện tử thời trang Việt Nam  
**Giai đoạn**: 04/07/2012 → 01/07/2024

---

##  Vấn Đề Bài Toán

### Bối cảnh kinh doanh
Một công ty thương mại điện tử thời trang Việt Nam cần **dự báo doanh thu (Revenue)** và **giá vốn hàng bán (COGS)** ở mức chi tiết theo ngày. Mục đích là tối ưu hoá:
- Phân bổ tồn kho
- Lập kế hoạch khuyến mãi  
- Quản lý logistics trên toàn quốc

### Các phần thi
| Phần | Tên | Điểm | Nội dung |
|------|-----|------|---------|
| **1** | Câu hỏi Trắc nghiệm (MCQ) | 20% | 10 câu hỏi phân tích dữ liệu |
| **2** | Trực quan hoá & EDA | 60% | Biểu đồ + Insights kinh doanh |
| **3** | Mô hình Dự báo (Forecasting) | 20% | Dự báo Revenue & COGS |

---

## Cấu Trúc Thư Mục

```
push_code/
│
├── 📄 README.md .......................... File này
├── 📄 requirements.txt ................... Danh sách thư viện cần cài
├── 📄 submission.csv ..................... File nộp bài cuối cùng (output)
│
├── 📂 Phan 1 Cau hoi Trac nghiem/ ........ PHẦN 1: Multiple Choice Questions
│   ├── data/ ............................ Dữ liệu gốc (15 file CSV)
│   │   ├── customers.csv, products.csv, promotions.csv, geography.csv
│   │   ├── orders.csv, order_items.csv, payments.csv, shipments.csv
│   │   ├── returns.csv, reviews.csv, sales.csv, inventory.csv
│   │   ├── web_traffic.csv, sample_submission.csv
│   │   └── [Tất cả dữ liệu tham khảo cho bài toán]
│   │
│   └── Sources/ ......................... Jupyter Notebooks (Q1-Q10)
│       ├── q1.ipynb ..................... Q1: Inter-order gap (trung vị)
│       ├── q2.ipynb ..................... Q2: Gross profit margin by segment
│       ├── q3.ipynb ..................... Q3: Return reasons for Streetwear
│       ├── q4.ipynb ..................... Q4: Traffic source bounce rate
│       ├── q5.ipynb ..................... Q5: Promotional items %
│       ├── q6.ipynb ..................... Q6: Orders/customer by age group
│       ├── q7.ipynb ..................... Q7: Revenue by region
│       ├── q8.ipynb ..................... Q8: Payment methods (cancelled)
│       ├── q9.ipynb ..................... Q9: Return rate by size
│       └── q10.ipynb .................... Q10: Payment value by installments
│
├── 📂 Phan 2 Truc quan hoa va Phan tich du lieu/ ... PHẦN 2: EDA & Visualization
│   │
│   ├── 📂 Gen_charts_2/ ................. Biểu đồ Plotly (Tương tác) — [CHẠY TRƯỚC]
│   │   ├── data/ ........................ Dữ liệu gốc (15 file CSV)
│   │   ├── sources/ ..................... Scripts chính
│   │   │   ├── merge_master.ipynb ...... [RUN 1st] Tạo master data từ 15 files
│   │   │   ├── create_plotly_charts.py . [RUN 3rd] Tạo biểu đồ Plotly cơ bản
│   │   │   ├── generate_all_charts.py .. [RUN 4th] Tạo toàn bộ biểu đồ
│   │   │   ├── web_traffic_analysis.py . [RUN 5th] Phân tích lưu lượng truy cập
│   │   │   └── plotly_visualizations.ipynb ... Visualisation tương tác
│   │   └── charts/ ....................... Output: HTML + PNG files
│   │
│   └── 📂 Gen_charts_1/ ................. Biểu đồ Matplotlib (Chi tiết) — [CHẠY SAU]
│       ├── data/ ........................ Dữ liệu đầu vào
│       │   ├── preprocessing.py ........ [RUN 2nd] Xử lý master data → master_data_final.csv
│       │   └── (Cần copy master data từ Gen_charts_2 vào đây trước)
│       │
│       ├── charts_stage_1/ ............. Stage 1: Biểu đồ 1-5 (Matplotlib)
│       │   ├── master_charts.py ........ [RUN] Chạy để tạo 5 biểu đồ đầu tiên
│       │   └── figure/ ................. Output: 5 PNG files
│       │
│       └── charts_stage_2/ ............. Stage 2: Biểu đồ 14 (Matplotlib)
│           ├── master_charts_1_to_13_code.py ... Biểu đồ 1-13 (code reference)
│           ├── charts_14.py ............ [RUN] Chạy để tạo biểu đồ 14
│           └── figure/ ................. Output: 1 PNG file
│
├── 📂 Phan 3 Mo hinh Du bao Doanh thu/ .. PHẦN 3: Sales Forecasting Model
│   ├── data_raw/ ........................ Dữ liệu gốc (15 file CSV)
│   │   ├── [Tất cả CSV từ cuộc thi]
│   │   └── sample_submission.csv ....... Format file nộp
│   │
│   ├── 🔹 STAGE 1: stage1_preprocessing.ipynb
│   │   ├── Input  : 15 file CSV gốc
│   │   ├── Task   : Load → Clean → Outlier detection → Feature aggregation
│   │   └── Output : master_clean.csv (~3800 rows)
│   │
│   ├── 🔹 STAGE 2: stage2_feature_engineering.ipynb
│   │   ├── Input  : master_clean.csv
│   │   ├── Task   : Create lag, rolling, calendar, Fourier, promo features
│   │   ├── Output : features_ready.csv + feature_meta.json
│   │   └── Note   : Tất cả features từ training data (NO LEAKAGE)
│   │
│   ├── 🔹 STAGE 3: stage3_model_training.ipynb
│   │   ├── Input  : features_ready.csv + feature_meta.json
│   │   ├── Task   : Prophet (trend) + LightGBM + CatBoost (residual)
│   │   ├── Models :
│   │   │   ├── lgbm_rev.pkl + lgbm_cogs.pkl
│   │   │   ├── catboost_rev.cbm + catboost_cogs.cbm
│   │   │   └── prophet_rev.pkl + prophet_cogs.pkl
│   │   └── Output : oof_predictions.csv (backtest 2021-2022)
│   │             + test_predictions.csv (test period 2023-2024)
│   │
│   ├── 🔹 STAGE 4: stage4_ensemble.ipynb
│   │   ├── Input  : oof_predictions.csv + test_predictions.csv
│   │   ├── Task   : Optimize blend weights (LGBM vs CatBoost)
│   │   ├── Output : ensemble_predictions.csv + ensemble_weights.json
│   │   └── Note   : MAE-based optimization
│   │
│   ├── 🔹 STAGE 5: stage5_shap.ipynb
│   │   ├── Input  : Ensemble models + features_ready.csv
│   │   ├── Task   : Calculate SHAP values → Feature importance analysis
│   │   └── Output : Plots in report/images/
│   │             (shap_summary_rev.png, shap_bar_rev.png, etc.)
│   │
│   ├── 🔹 STAGE 6: stage6_submission.ipynb
│   │   ├── Input  : ensemble_predictions.csv + sample_submission.csv
│   │   ├── Task   : Align predictions → Format validation → Save submission
│   │   └── Output : ../submission.csv (FINAL FILE FOR KAGGLE)
│
└── 📂 .gitignore ......................... Git ignore rules

```

### Giải thích chi tiết từng thư mục

**Phần 1 — Câu hỏi Trắc nghiệm (MCQ)**
- 10 file Jupyter notebook `q1.ipynb` - `q10.ipynb`
- Mỗi file giải quyết một câu hỏi bằng cách query dữ liệu

**Phần 2 — Trực quan hoá & EDA**
- **Gen_charts_2**: Biểu đồ Plotly (plotly) → HTML + PNG tương tác
  - ✅ **CHẠY TRƯỚC TIÊN**: `merge_master.ipynb` → tạo file master data từ 15 CSV files
  - Sau đó chạy `create_plotly_charts.py` + `generate_all_charts.py` + `web_traffic_analysis.py`
- **Gen_charts_1**: Biểu đồ Matplotlib (matplotlib, seaborn) → PNG
  - ✅ **BƯỚC 1**: Copy file master data từ Gen_charts_2 vào `Gen_charts_1/data/`
  - **BƯỚC 2**: Chạy `preprocessing.py` để tạo `master_data_final.csv`
  - **BƯỚC 3**: Chạy `master_charts.py` (stage_1) tạo 5 biểu đồ
  - **BƯỚC 4**: Chạy `charts_14.py` (stage_2) tạo biểu đồ 14

**Phần 3 — Mô hình Dự báo (Forecasting)**
- **6 Stages tuần tự** (phải chạy lần lượt):
  1. **Stage 1**: Xử lý dữ liệu gốc
  2. **Stage 2**: Tạo features
  3. **Stage 3**: Huấn luyện models
  4. **Stage 4**: Blend/Ensemble
  5. **Stage 5**: Giải thích bằng SHAP
  6. **Stage 6**: Tạo file submission.csv

---

##  Hướng dẫn Sử dụng

###  Bước 0: Cài đặt Môi trường

#### Yêu cầu
- **Python 3.8+** (khuyến nghị 3.9 hoặc 3.10)
- **pip** 

#### Sử dụng Virtual Environment (Khuyến nghị)

```bash
# Tạo thư mục làm việc
cd d:\your_folder

# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Nâng cấp pip
pip install --upgrade pip

# Cài đặt tất cả thư viện từ requirements.txt
pip install -r requirements.txt

# Xác nhận cài đặt thành công
python -c "import pandas, numpy, lightgbm, prophet, shap; print('✓ All libraries installed!')"
```

###  PHẦN 3: Mô Hình Dự báo Doanh thu (BUILD MODEL)

**Mục tiêu**: Dự báo Revenue & COGS từ 01/01/2023 - 01/07/2024

#### 🔹 Cấu trúc Thư mục Phần 3
```
Phan 3 Mo hinh Du bao Doanh thu/
├── data_raw/ ........................... 15 file CSV gốc
├── stage1_preprocessing.ipynb ........... [RUN 1]
├── stage2_feature_engineering.ipynb .... [RUN 2]
├── stage3_model_training.ipynb ......... [RUN 3]
├── stage4_ensemble.ipynb ............... [RUN 4]
├── stage5_shap.ipynb ................... [RUN 5]
├── stage6_submission.ipynb ............. [RUN 6]
└── report/ ............................ Báo cáo & hình ảnh
```

####  Chạy 6 Stages tuần tự

**Stage 1: Xử lý Dữ liệu (Preprocessing)**
```bash
# Mở Jupyter Notebook
jupyter notebook "Phan 3 Mo hinh Du bao Doanh thu/stage1_preprocessing.ipynb"

# Hoặc sử dụng VS Code
code "Phan 3 Mo hinh Du bao Doanh thu/stage1_preprocessing.ipynb"

# Task:
# 1. Load 15 file CSV từ data_raw/
# 2. Inspect & clean dữ liệu (missing values, outliers)
# 3. Detect structural break (2019)
# 4. Merge web_traffic vào sales
# 5. Save: master_clean.csv
```

**Stage 2: Feature Engineering**
```bash
jupyter notebook "Phan 3 Mo hinh Du bao Doanh thu/stage2_feature_engineering.ipynb"

# Task:
# 1. Load master_clean.csv
# 2. Create features:
#    - Lag features (7, 14, 28, 30, 60, 90, 180, 365 ngày)
#    - Rolling statistics (mean, std, min, max)
#    - Calendar features (month, day_of_week, quarter, etc.)
#    - Fourier terms (sin/cos cho chu kỳ 7 & 365 ngày)
#    - Promo indicators
#    - Web traffic lags
# 3. NO LEAKAGE: Tất cả lags ≥ 1
# 4. Save: features_ready.csv + feature_meta.json
```

**Stage 3: Model Training**
```bash
jupyter notebook "Phan 3 Mo hinh Du bao Doanh thu/stage3_model_training.ipynb"

# Task:
# 1. Load features_ready.csv
# 2. Train 3 models cho Revenue & COGS:
#    - Prophet (trend + seasonality)
#    - LightGBM (residual learning)
#    - CatBoost (residual learning)
# 3. Backtest: 2021-01-01 → 2022-12-31
# 4. Forecast: 2023-01-01 → 2024-07-01
# 5. Save models: lgbm_rev.pkl, catboost_rev.cbm, prophet_rev.pkl (cùng cho COGS)
# 6. Output: oof_predictions.csv + test_predictions.csv
```

**Stage 4: Ensemble Blending**
```bash
jupyter notebook "Phan 3 Mo hinh Du bao Doanh thu/stage4_ensemble.ipynb"

# Task:
# 1. Load oof_predictions.csv (backtest) + test_predictions.csv
# 2. Compare 3 baseline: Prophet, Prophet+LGBM, Prophet+CatBoost
# 3. Optimize blend weights:
#    - Objective: Minimize MAE on holdout (2021-2022)
#    - Constraint: weights sum to 1.0, all >= 0
# 4. Apply weights to test predictions
# 5. Save: ensemble_predictions.csv + ensemble_weights.json
```

**Stage 5: SHAP Explainability**
```bash
jupyter notebook "Phan 3 Mo hinh Du bao Doanh thu/stage5_shap.ipynb"

# Task:
# 1. Load trained models: lgbm_rev.pkl + catboost_rev.cbm
# 2. Calculate SHAP values (TreeExplainer)
# 3. Generate plots:
#    - Summary plot (feature importance)
#    - Bar plot (mean |SHAP|)
#    - Dependence plots (top 3 features)
# 4. Save to: report/images/
```

**Stage 6: Final Submission**
```bash
jupyter notebook "Phan 3 Mo hinh Du bao Doanh thu/stage6_submission.ipynb"

# Task:
# 1. Load ensemble_predictions.csv
# 2. Align by Date với sample_submission.csv (maintain row order!)
# 3. Select final columns: Date, Revenue, COGS
# 4. Validate:
#    ✓ 548 rows (01/01/2023 - 01/07/2024)
#    ✓ No NaN values
#    ✓ Revenue/COGS > 0
# 5. Save: ../submission.csv
# 6. Upload lên Kaggle
```

#### Output cuối cùng (Stage 6)
```
../submission.csv
├── Date (YYYY-MM-DD format)
├── Revenue (float, 2 decimal places)
└── COGS (float, 2 decimal places)

Ví dụ:
Date,Revenue,COGS
2023-01-01,26607.20,2585.15
2023-01-02,1007.89,163.00
...
2024-07-01,54321.78,5432.10
```

---

###  PHẦN 2: Trực quan hoá & Phân tích EDA

**Mục tiêu**: Tạo 16+ biểu đồ với insights kinh doanh

#### 🔹 Cấu trúc Phần 2

```
   📂 Phan 2 Truc quan hoa va Phan tich du lieu/ ... PHẦN 2: EDA & Visualization
   │
   ├── 📂 Gen_charts_2/ ................. Biểu đồ Plotly (Tương tác) — [CHẠY TRƯỚC]
   │   ├── data/ ........................ Dữ liệu gốc (15 file CSV)
   │   ├── sources/ ..................... Scripts chính
   │   │   ├── merge_master.ipynb ...... [RUN 1st] Tạo master data từ 15 files
   │   │   ├── create_plotly_charts.py . [RUN 3rd] Tạo biểu đồ Plotly cơ bản
   │   │   ├── generate_all_charts.py .. [RUN 4th] Tạo toàn bộ biểu đồ
   │   │   ├── web_traffic_analysis.py . [RUN 5th] Phân tích lưu lượng truy cập
   │   │   └── plotly_visualizations.ipynb ... Visualisation tương tác
   │   └── charts/ ....................... Output: HTML + PNG files
   │
   └── 📂 Gen_charts_1/ ................. Biểu đồ Matplotlib (Chi tiết) — [CHẠY SAU]
       ├── data/ ........................ Dữ liệu đầu vào
       │   ├── preprocessing.py ........ [RUN 2nd] Xử lý master data → master_data_final.csv
       │   └── (Cần copy master data từ Gen_charts_2 vào đây trước)
       │
       ├── charts_stage_1/ ............. Stage 1: Biểu đồ 1-5 (Matplotlib)
       │   ├── master_charts.py ........ [RUN] Chạy để tạo 5 biểu đồ đầu tiên
       │   └── figure/ ................. Output: 5 PNG files
       │
       └── charts_stage_2/ ............. Stage 2: Biểu đồ 14 (Matplotlib)
           ├── master_charts_1_to_13_code.py ... Biểu đồ 1-13 (code reference)
           ├── charts_14.py ............ [RUN] Chạy để tạo biểu đồ 14
           └── figure/ ................. Output: 1 PNG file

```

####  Chạy Phần 2

**Bước 0: Gen_charts_2 - Tạo Master Data (CHẠY TRƯỚC)**

```bash
# Mở Jupyter Notebook
cd "Phan 2 Truc quan hoa va Phan tich du lieu/Gen_charts_2/sources"
jupyter notebook merge_master.ipynb

# Task:
# - Load & merge 15 CSV files từ ../data/
# - Tạo file master data (trong bộ nhớ hoặc lưu tạm)
# - OUTPUT: File master data sẽ được dùng cho Gen_charts_1
```

**Bước 1: Gen_charts_1 - Xử lý & Matplotlib (CÓ ĐƯA MASTER DATA VÀO)**

```bash
# 1a. Copy/Lấy file master data vào Gen_charts_1/data/
# (File master data từ merge_master.ipynb ở Gen_charts_2)
cd "Phan 2 Truc quan hoa va Phan tich du lieu/Gen_charts_1/data"

# 1b. Chạy preprocessing.py để xử lý data
python preprocessing.py

# Output: master_data_final.csv
# Check: ~3000+ rows, columns gồm order_date, quantity, unit_price, cogs, etc.

# 1c. Chạy biểu đồ Stage 1 (5 biểu đồ đầu tiên)
cd ../charts_stage_1
python master_charts.py

# Output: 5 PNG files trong folder figure/

# 1d. Chạy biểu đồ Stage 2 (biểu đồ 14)
cd ../charts_stage_2
python charts_14.py

# Output: 14 PNG file trong folder figure/
```

**Bước 2: Gen_charts_2 - Plotly Charts (TIẾP THEO)**

```bash
# 2a. Tạo Plotly biểu đồ cơ bản
cd "Phan 2 Truc quan hoa va Phan tich du lieu/Gen_charts_2/sources"
python create_plotly_charts.py

# Output: HTML & PNG files trong ../charts/

# 2b. Tạo tất cả Plotly biểu đồ
python generate_all_charts.py

# Output: Thêm HTML & PNG files

# 2c. Phân tích lưu lượng truy cập
python web_traffic_analysis.py

# Output: Thêm HTML & PNG files
```

#### Output Phần 2
- **Gen_charts_1/figure/**: 16 PNG files (matplotlib)
- **Gen_charts_2/charts/**: 10+ HTML + PNG files (plotly)

---

###  PHẦN 1: Câu hỏi Trắc nghiệm (MCQ)

**Mục tiêu**: Trả lời 10 câu hỏi bằng phân tích dữ liệu

#### 🔹 Cấu trúc Phần 1
```
Phan 1 Cau hoi Trac nghiem/
├── data/ ............................ 15 CSV files (data gốc)
└── Sources/
    ├── q1.ipynb ..................... Q1: Inter-order gap
    ├── q2.ipynb ..................... Q2: Gross profit margin
    ├── q3.ipynb ..................... Q3: Return reasons
    ├── q4.ipynb ..................... Q4: Traffic bounce rate
    ├── q5.ipynb ..................... Q5: Promotional %
    ├── q6.ipynb ..................... Q6: Orders by age group
    ├── q7.ipynb ..................... Q7: Revenue by region
    ├── q8.ipynb ..................... Q8: Payment methods
    ├── q9.ipynb ..................... Q9: Return rate by size
    └── q10.ipynb .................... Q10: Payment by installments
```

####  Chạy từng câu hỏi

```bash
# Mở Jupyter Notebook
cd "Phan 1 Cau hoi Trac nghiem/Sources"

# Chạy từng file
jupyter notebook q1.ipynb   # Q1
jupyter notebook q2.ipynb   # Q2
# ... và cứ tiếp tục với q3-q10

# Hoặc sử dụng VS Code
code q1.ipynb

# Mỗi file sẽ:
# 1. Load dữ liệu từ ../data/
# 2. Thực hiện query/phân tích cần thiết
# 3. In ra kết quả & câu trả lời
# 4. Print câu trả lời ngoài cùng (A/B/C/D)
```

#### Ví dụ Q1
```python
# Q1: Inter-order gap (trung vị ngày giữa 2 lần mua)

import pandas as pd
orders = pd.read_csv('../data/orders.csv', parse_dates=['order_date'])
orders = orders.sort_values(['customer_id', 'order_date'])

# Tìm customer có 2+ orders
multi_order = orders.groupby('customer_id').size()
multi_order = multi_order[multi_order >= 2].index

# Tính gap
gaps = orders[orders['customer_id'].isin(multi_order)]\
    .groupby('customer_id')['order_date'].diff().dt.days

median_gap = gaps.dropna().median()
print(f"Trung vị gap: {median_gap} ngày")
# Output: 144 ngày → Câu trả lời: C
```

#### Output Phần 1
- Mỗi notebook sẽ in ra kết quả: **A, B, C, hoặc D**
- Ghi lại 10 đáp án này để submit vào form chính thức


## Troubleshooting

### Lỗi: `ModuleNotFoundError: No module named 'pandas'`
```bash
# Đảm bảo virtual environment được kích hoạt
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Cài lại requirements
pip install -r requirements.txt
```

### Lỗi: `FileNotFoundError: data/orders.csv`
```bash
# Đảm bảo đang ở đúng directory
# Phần 1: cd Phan\ 1\ Cau\ hoi\ Trac\ nghiem/Sources/
# Phần 3: cd Phan\ 3\ Mo\ hinh\ Du\ bao\ Doanh\ thu/
```

### Lỗi: `prophet` không cài được
```bash
# Thường xảy ra trên Windows
pip install --upgrade pip setuptools wheel
pip install pystan==2.19.1.1
pip install prophet
```

### Lỗi: Plotly không lưu PNG
```bash
# Cần kaleido
pip install kaleido>=0.2.1
```
## 🎓 Tài liệu Tham khảo

- **Pandas Documentation**: https://pandas.pydata.org/docs/
- **LightGBM**: https://lightgbm.readthedocs.io/
- **CatBoost**: https://catboost.ai/en/docs/
- **Prophet**: https://facebook.github.io/prophet/
- **SHAP**: https://shap.readthedocs.io/
- **Plotly**: https://plotly.com/python/

---

## Checklist Chạy Dự Án

- [ ] Cài requirements.txt
- [ ] **Phần 3**: Chạy 6 stages tuần tự
  - [ ] Stage 1: preprocessing
  - [ ] Stage 2: feature engineering
  - [ ] Stage 3: model training
  - [ ] Stage 4: ensemble
  - [ ] Stage 5: SHAP
  - [ ] Stage 6: submission
- [ ] **Phần 2**: Chạy EDA
  - [ ] Gen_charts_1
  - [ ] Gen_charts_2
- [ ] **Phần 1**: Trả lời 10 MCQ
- [ ] Kiểm tra submission.csv (548 rows, 3 columns)
- [ ] Nộp bài trên Kaggle

## Liên hệ & Hỗ trợ

**Email**: cn20378@gmail.com  

**Last Updated**: May 2026  
**Author**: Entropy Tetra 
