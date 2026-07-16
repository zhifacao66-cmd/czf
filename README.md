# 电商用户行为数据分析

## 📋 项目简介

本项目对某电商平台 2024 年用户行为数据进行多维度分析，涵盖用户留存、转化漏斗、RFM 模型、用户分群等核心分析场景，旨在为运营决策提供数据支撑。

## 🎯 分析目标

- **用户增长分析**：日活 / 周活 / 月活趋势
- **转化漏斗分析**：浏览 → 加购 → 下单 → 支付转化率
- **用户留存分析**：次日 / 7日 / 30日留存率
- **RFM 用户分层**：按最近消费、频率、金额划分用户价值
- **商品品类分析**：Top 品类销量与销售额分布

## 🛠 技术栈

| 层级 | 技术 |
|------|------|
| 语言 | Python 3.10+ |
| 数据处理 | Pandas, NumPy |
| 可视化 | Matplotlib, Seaborn, Plotly |
| 统计分析 | SciPy |
| 环境管理 | conda / venv |

## 📁 项目结构

```
ecommerce-analysis/
├── data/                # 数据集（生成脚本 + CSV）
├── notebooks/           # Jupyter Notebook 分析文件
├── images/              # 可视化图表输出
├── reports/             # 分析报告
├── requirements.txt     # Python 依赖
└── README.md
```

## 🚀 快速开始

```bash
# 1. 克隆项目
git clone git@github.com:zhifacao66-cmd/czf.git
cd czf

# 2. 创建虚拟环境
python -m venv venv
# Windows: venv\Scripts\activate
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 生成模拟数据
python data/generate_data.py

# 5. 运行完整分析
python notebooks/analysis.py

# 6. 启动 Jupyter（可选）
jupyter notebook notebooks/
```

## 📊 分析结果展示

### 用户增长趋势
![用户增长](./images/user_growth.png)

### 转化漏斗
![转化漏斗](./images/funnel.png)

### RFM 用户分层
![RFM](./images/rfm.png)

### 品类分析
![品类分析](./images/category_analysis.png)

## 📝 核心发现

1. **转化率瓶颈在加购→下单环节**（~35%），优化购物车体验是关键
2. **高价值用户占比 15%** 但贡献了 **58% 的 GMV**
3. **30日留存仅 12%**，建议加强会员体系和精准推送
4. **周末是流量高峰**，建议将大促活动安排在周六

## 📄 License

MIT License
