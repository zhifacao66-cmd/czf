# -*- coding: utf-8 -*-
"""
电商用户行为数据分析 - 主分析文件
包含：数据概览、日活趋势、转化漏斗、留存分析、RFM模型、品类分析
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
import warnings
warnings.filterwarnings("ignore")

# ── 中文字体设置 ──
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
sns.set_style("whitegrid")
sns.set_palette("Set2")

os.makedirs("../images", exist_ok=True)

# ═══════════════════════════════════════════
# 1. 数据加载与清洗
# ═══════════════════════════════════════════
print("=" * 60)
print("1. 数据加载与清洗")
print("=" * 60)

df = pd.read_csv("../data/user_behavior.csv", parse_dates=["timestamp"])
print(f"原始数据量: {len(df):,} 条")
print(f"时间范围: {df['timestamp'].min()} ~ {df['timestamp'].max()}")

# 缺失值检查
missing = df.isnull().sum()
print(f"\n缺失值检查:\n{missing[missing > 0] if missing.sum() > 0 else '无缺失值'}")

# 去重
df.drop_duplicates(inplace=True)
print(f"去重后数据量: {len(df):,} 条")

# ═══════════════════════════════════════════
# 2. 用户增长与活跃度分析
# ═══════════════════════════════════════════
print("\n" + "=" * 60)
print("2. 用户增长与活跃度分析")
print("=" * 60)

df["date"] = df["timestamp"].dt.date

# 日活 (DAU)
dau = df.groupby("date")["user_id"].nunique().reset_index()
dau.columns = ["date", "dau"]

# 周活 (WAU)
dau["date"] = pd.to_datetime(dau["date"])
dau["week"] = dau["date"].dt.isocalendar().week.astype(int)
wau = dau.groupby("week")["dau"].sum().reset_index()
wau.columns = ["week", "wau"]

# 月活 (MAU)
dau["month"] = dau["date"].dt.month
mau = dau.groupby("month")["dau"].sum().reset_index()
mau.columns = ["month", "mau"]

print(f"平均日活: {dau['dau'].mean():.0f}")
print(f"最高日活: {dau['dau'].max()}")
print(f"平均周活: {wau['wau'].mean():.0f}")

# 日活趋势图
fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(dau["date"], dau["dau"], color="#2196F3", linewidth=1.2)
ax.fill_between(dau["date"], dau["dau"], alpha=0.15, color="#2196F3")
ax.axhline(dau["dau"].mean(), color="red", linestyle="--", alpha=0.7, label=f'均值: {dau["dau"].mean():.0f}')
ax.set_title("日活跃用户趋势 (DAU)", fontsize=16, fontweight="bold")
ax.set_xlabel("日期")
ax.set_ylabel("活跃用户数")
ax.legend()
plt.tight_layout()
fig.savefig("../images/user_growth.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ 图表已保存: images/user_growth.png")

# ═══════════════════════════════════════════
# 3. 转化漏斗分析
# ═══════════════════════════════════════════
print("\n" + "=" * 60)
print("3. 转化漏斗分析")
print("=" * 60)

funnel_stages = ["pv", "fav", "cart", "buy", "pay"]
funnel_labels = ["浏览", "收藏", "加购", "下单", "支付"]

funnel_counts = []
for b in funnel_stages:
    cnt = df[df["behavior_type"] == b]["user_id"].nunique()
    funnel_counts.append(cnt)

funnel_df = pd.DataFrame({"阶段": funnel_labels, "用户数": funnel_counts})
funnel_df["总体转化率"] = (funnel_df["用户数"] / funnel_df["用户数"].iloc[0] * 100).round(2)
funnel_df["环节转化率"] = [100.0] + [
    round(funnel_df["用户数"].iloc[i] / funnel_df["用户数"].iloc[i - 1] * 100, 2)
    for i in range(1, len(funnel_df))
]

print(funnel_df.to_string(index=False))

# 漏斗图
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

colors = ["#42A5F5", "#66BB6A", "#FFA726", "#EF5350", "#AB47BC"]
bars = ax1.barh(funnel_labels, funnel_counts, color=colors, edgecolor="white")
ax1.set_title("转化漏斗 - 各阶段用户数", fontsize=14, fontweight="bold")
ax1.set_xlabel("用户数")
ax1.invert_yaxis()
for bar, cnt in zip(bars, funnel_counts):
    ax1.text(bar.get_width() + 50, bar.get_y() + bar.get_height() / 2,
             f"{cnt:,}", va="center", fontsize=11, fontweight="bold")

ax2.plot(funnel_labels, funnel_df["环节转化率"], marker="o", linewidth=2,
         markersize=10, color="#EF5350")
ax2.fill_between(range(len(funnel_labels)), funnel_df["环节转化率"], alpha=0.1, color="#EF5350")
ax2.set_title("各环节转化率变化", fontsize=14, fontweight="bold")
ax2.set_ylabel("环节转化率 (%)")
ax2.set_ylim(0, 110)
for i, rate in enumerate(funnel_df["环节转化率"]):
    ax2.annotate(f"{rate}%", (i, rate), textcoords="offset points",
                 xytext=(0, 12), ha="center", fontsize=10, fontweight="bold")

plt.tight_layout()
fig.savefig("../images/funnel.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ 图表已保存: images/funnel.png")

# ═══════════════════════════════════════════
# 4. 用户留存分析
# ═══════════════════════════════════════════
print("\n" + "=" * 60)
print("4. 用户留存分析")
print("=" * 60)

# 按用户找首次活跃日期
first_active = df.groupby("user_id")["date"].min().reset_index()
first_active.columns = ["user_id", "first_date"]
first_active["first_date"] = pd.to_datetime(first_active["first_date"])

df_merged = df.merge(first_active, on="user_id")
df_merged["day_offset"] = (df_merged["date"] - df_merged["first_date"]).dt.days

# 计算留存率
retention_days = [1, 3, 7, 14, 30]
total_users = df["user_id"].nunique()
retention_rates = []

for day_n in retention_days:
    retained = df_merged[df_merged["day_offset"] == day_n]["user_id"].nunique()
    rate = round(retained / total_users * 100, 2)
    retention_rates.append(rate)
    print(f"  Day-{day_n:2d} 留存: {rate}%")

# 留存曲线
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(retention_days, retention_rates, marker="s", linewidth=2.5,
        markersize=10, color="#FF5722")
ax.fill_between(retention_days, retention_rates, alpha=0.1, color="#FF5722")
ax.set_title("用户留存曲线", fontsize=16, fontweight="bold")
ax.set_xlabel("距首次活跃天数")
ax.set_ylabel("留存率 (%)")
ax.set_xticks(retention_days)
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f%%"))
for x, y in zip(retention_days, retention_rates):
    ax.annotate(f"{y}%", (x, y), textcoords="offset points",
                xytext=(0, 10), ha="center", fontsize=11, fontweight="bold")
plt.tight_layout()
fig.savefig("../images/retention.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ 图表已保存: images/retention.png")

# ═══════════════════════════════════════════
# 5. RFM 用户分层
# ═══════════════════════════════════════════
print("\n" + "=" * 60)
print("5. RFM 用户分层模型")
print("=" * 60)

# 只对已支付用户计算RFM
pay_users = df[df["behavior_type"] == "pay"].copy()
now = df["timestamp"].max()

rfm = pay_users.groupby("user_id").agg(
    last_pay=("timestamp", "max"),
    frequency=("behavior_id", "count"),
    monetary=("price", "sum")
).reset_index()

rfm["recency"] = (now - rfm["last_pay"]).dt.days
rfm = rfm[["user_id", "recency", "frequency", "monetary"]]

# 分位数打分
rfm["R_score"] = pd.qcut(rfm["recency"], q=4, labels=[4, 3, 2, 1])
rfm["F_score"] = pd.qcut(rfm["frequency"].rank(method="first"), q=4, labels=[1, 2, 3, 4])
rfm["M_score"] = pd.qcut(rfm["monetary"].rank(method="first"), q=4, labels=[1, 2, 3, 4])

rfm["RFM_score"] = rfm["R_score"].astype(int) + rfm["F_score"].astype(int) + rfm["M_score"].astype(int)

def label_rfm(score):
    if score >= 10:
        return "高价值用户"
    elif score >= 8:
        return "重要发展用户"
    elif score >= 6:
        return "重要保持用户"
    elif score >= 4:
        return "一般用户"
    else:
        return "流失用户"

rfm["segment"] = rfm["RFM_score"].apply(label_rfm)
segment_counts = rfm["segment"].value_counts()

print("\n用户分层结果:")
for seg, cnt in segment_counts.items():
    print(f"  {seg}: {cnt} ({cnt / len(rfm) * 100:.1f}%)")

# RFM散点图
fig, ax = plt.subplots(figsize=(10, 6))
palette = {
    "高价值用户": "#4CAF50",
    "重要发展用户": "#2196F3",
    "重要保持用户": "#FF9800",
    "一般用户": "#9E9E9E",
    "流失用户": "#f44336",
}
for seg in palette:
    subset = rfm[rfm["segment"] == seg]
    ax.scatter(subset["recency"], subset["monetary"],
               c=palette[seg], label=seg, alpha=0.6, s=30)
ax.set_title("RFM 用户分层 - 最近消费 vs 消费金额", fontsize=14, fontweight="bold")
ax.set_xlabel("Recency (天)")
ax.set_ylabel("Monetary (元)")
ax.legend(loc="upper right")
plt.tight_layout()
fig.savefig("../images/rfm.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ 图表已保存: images/rfm.png")

# ═══════════════════════════════════════════
# 6. 品类分析
# ═══════════════════════════════════════════
print("\n" + "=" * 60)
print("6. 商品品类分析")
print("=" * 60)

category_stats = df.groupby("category").agg(
    pv=("behavior_id", "count"),
    avg_price=("price", "mean"),
    buy_count=("behavior_type", lambda x: (x == "pay").sum()),
    revenue=("price", lambda x: x[df.loc[x.index, "behavior_type"] == "pay"].sum())
).reset_index()

category_stats["转化率"] = (category_stats["buy_count"] / category_stats["pv"] * 100).round(2)
category_stats = category_stats.sort_values("pv", ascending=False)

print(category_stats.to_string(index=False))

# 品类排行
fig, axes = plt.subplots(1, 2, figsize=(14, 7))

# 流量Top
top10 = category_stats.head(10)
bars = axes[0].barh(top10["category"], top10["pv"], color="#42A5F5", edgecolor="white")
axes[0].set_title("品类浏览量 Top 10", fontsize=14, fontweight="bold")
axes[0].set_xlabel("浏览次数")
axes[0].invert_yaxis()
for bar, v in zip(bars, top10["pv"]):
    axes[0].text(bar.get_width() + 100, bar.get_y() + bar.get_height() / 2,
                 f"{v:,}", va="center", fontsize=9)

# 转化率
sorted_conv = category_stats.sort_values("转化率", ascending=False)
bars2 = axes[1].barh(sorted_conv["category"], sorted_conv["转化率"], color="#66BB6A", edgecolor="white")
axes[1].set_title("各品类支付转化率", fontsize=14, fontweight="bold")
axes[1].set_xlabel("转化率 (%)")
axes[1].invert_yaxis()
for bar, v in zip(bars2, sorted_conv["转化率"]):
    axes[1].text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                 f"{v:.1f}%", va="center", fontsize=9)

plt.tight_layout()
fig.savefig("../images/category_analysis.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ 图表已保存: images/category_analysis.png")

# ═══════════════════════════════════════════
# 7. 时段分析
# ═══════════════════════════════════════════
print("\n" + "=" * 60)
print("7. 用户行为时段分析")
print("=" * 60)

hourly = df.groupby(["hour", "behavior_type"]).size().unstack(fill_value=0)

fig, ax = plt.subplots(figsize=(14, 5))
behavior_colors = {"pv": "#42A5F5", "fav": "#FFCA28", "cart": "#66BB6A",
                   "buy": "#EF5350", "pay": "#AB47BC"}
labels_cn = {"pv": "浏览", "fav": "收藏", "cart": "加购", "buy": "下单", "pay": "支付"}

for b in ["pv", "fav", "cart", "buy", "pay"]:
    ax.plot(hourly.index, hourly[b], color=behavior_colors[b],
            label=labels_cn[b], linewidth=1.8)

ax.set_title("用户行为时段分布 (24小时)", fontsize=16, fontweight="bold")
ax.set_xlabel("小时")
ax.set_ylabel("行为次数")
ax.set_xticks(range(0, 24, 2))
ax.legend()
plt.tight_layout()
fig.savefig("../images/hourly.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ 图表已保存: images/hourly.png")

# ═══════════════════════════════════════════
# 8. 总结
# ═══════════════════════════════════════════
print("\n" + "=" * 60)
print("📊 分析完成！所有图表已保存到 images/ 目录")
print("=" * 60)
print(f"""
核心指标汇总:
  - 日活均值: {dau['dau'].mean():.0f}
  - 浏览→支付总体转化率: {funnel_df['总体转化率'].iloc[-1]}%
  - 次日留存: {retention_rates[0]}%
  - 7日留存: {retention_rates[retention_days.index(7)]}%
  - 30日留存: {retention_rates[-1]}%
  - 高价值用户占比: {segment_counts.get('高价值用户', 0) / len(rfm) * 100:.1f}%
""")
