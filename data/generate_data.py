"""
模拟电商数据集生成
产生 10 万条用户行为记录，涵盖浏览、收藏、加购、下单、支付五种行为
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

np.random.seed(42)

# ── 基本参数 ──
N_USERS = 3000
N_ITEMS = 2000
N_CATEGORIES = 12
N_DAYS = 90
START_DATE = datetime(2024, 1, 1)
BEHAVIOR_TYPES = ["pv", "fav", "cart", "buy", "pay"]
BEHAVIOR_WEIGHTS = [0.58, 0.08, 0.15, 0.13, 0.06]

CATEGORIES = [
    "手机数码", "家用电器", "服饰鞋包", "美妆个护",
    "食品生鲜", "家居家具", "母婴用品", "运动户外",
    "图书文娱", "汽车用品", "珠宝饰品", "医疗保健"
]

# ── 用户画像 ──
users = pd.DataFrame({
    "user_id": range(1, N_USERS + 1),
    "age": np.random.choice(["18-24", "25-34", "35-44", "45-54", "55+"],
                            N_USERS, p=[0.25, 0.35, 0.22, 0.12, 0.06]),
    "gender": np.random.choice(["M", "F"], N_USERS, p=[0.48, 0.52]),
    "city_tier": np.random.choice(["一线", "二线", "三线", "四线及以下"],
                                  N_USERS, p=[0.20, 0.30, 0.28, 0.22]),
    "register_date": [
        START_DATE - timedelta(days=int(d))
        for d in np.random.exponential(scale=365, size=N_USERS)
    ]
})

# ── 商品信息 ──
items = pd.DataFrame({
    "item_id": range(1, N_ITEMS + 1),
    "category": np.random.choice(CATEGORIES, N_ITEMS),
    "price": np.round(np.random.lognormal(mean=4.5, sigma=1.2, size=N_ITEMS), 2),
})

# ── 用户行为记录生成 ──
records = []
for day_idx in range(N_DAYS):
    date = START_DATE + timedelta(days=day_idx)
    day_of_week = date.weekday()  # 0=Monday
    day_factor = 1.0 + 0.3 * (day_of_week >= 5)  # 周末流量更高

    daily_users = min(
        N_USERS,
        int(np.random.normal(800 * day_factor, 120))
    )
    active_users = np.random.choice(users["user_id"], size=max(daily_users, 200), replace=True)

    for user_id in active_users:
        # 每个活跃用户的行为次数服从幂律分布
        n_behaviors = int(np.random.pareto(a=2.5)) + 1
        n_behaviors = min(n_behaviors, 8)

        for _ in range(n_behaviors):
            item_id = np.random.choice(items["item_id"])
            behavior = np.random.choice(BEHAVIOR_TYPES, p=BEHAVIOR_WEIGHTS)
            hour = int(np.random.triangular(7, 14, 23))
            minute = np.random.randint(0, 60)
            timestamp = date + timedelta(hours=hour, minutes=minute)

            records.append({
                "user_id": int(user_id),
                "item_id": int(item_id),
                "behavior_type": behavior,
                "timestamp": timestamp,
                "date": date.strftime("%Y-%m-%d"),
                "hour": hour,
                "day_of_week": day_of_week,
            })

df = pd.DataFrame(records)
df = df.sort_values("timestamp").reset_index(drop=True)
df["behavior_id"] = range(1, len(df) + 1)
df = df[["behavior_id", "user_id", "item_id", "behavior_type", "timestamp", "date", "hour", "day_of_week"]]

# ── 合并品类和价格 ──
df = df.merge(items, on="item_id", how="left")
df = df.merge(users, on="user_id", how="left")

# ── 保存 ──
os.makedirs("data", exist_ok=True)
df.to_csv("data/user_behavior.csv", index=False, encoding="utf-8-sig")
users.to_csv("data/users.csv", index=False, encoding="utf-8-sig")
items.to_csv("data/items.csv", index=False, encoding="utf-8-sig")

print(f"✅ 数据生成完毕！共 {len(df):,} 条行为记录")
print(f"   - 用户数: {N_USERS}")
print(f"   - 商品数: {N_ITEMS}")
print(f"   - 时间跨度: {START_DATE.date()} 至 {(START_DATE + timedelta(days=N_DAYS - 1)).date()}")
