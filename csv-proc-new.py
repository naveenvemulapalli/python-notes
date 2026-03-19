import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import datetime

# Directory containing CSV files
DATA_DIR = "./data"
OUTPUT_DIR = "./output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Date range
dates = [
    "9Mar", "10Mar", "11Mar", "12Mar", "13Mar",
    "14Mar", "15Mar", "16Mar", "17Mar", "18Mar", "19Mar"
]

daily_totals = []

# 👉 NEW: collect % data for pivot
all_pct_data = []

for d in dates:
    file_a = os.path.join(DATA_DIR, f"prod_products_regiona_{d}.csv")
    file_b = os.path.join(DATA_DIR, f"prod_products_regionb_{d}.csv")

    if not (os.path.exists(file_a) and os.path.exists(file_b)):
        print(f"Skipping {d}, file missing")
        continue

    # Read CSVs
    df_a = pd.read_csv(file_a)
    df_b = pd.read_csv(file_b)

    # Rename columns
    df_a.rename(columns={"count": "count_a"}, inplace=True)
    df_b.rename(columns={"count": "count_b"}, inplace=True)

    # Merge
    merged = pd.merge(df_a, df_b, on="product", how="outer")

    # Fill NaN
    merged.fillna(0, inplace=True)

    merged["count_a"] = merged["count_a"].astype(int)
    merged["count_b"] = merged["count_b"].astype(int)

    # Total count per product
    merged["total_count"] = merged["count_a"] + merged["count_b"]

    # 👉 NEW: calculate daily total
    daily_total = merged["total_count"].sum()

    # 👉 NEW: percentage column
    if daily_total > 0:
        merged["total_count_pct"] = (
            merged["total_count"] / daily_total * 100
        )
    else:
        merged["total_count_pct"] = 0

    # Save per-day CSV
    output_file = os.path.join(OUTPUT_DIR, f"combined_{d}.csv")
    merged.to_csv(output_file, index=False)

    print(f"Generated: {output_file}")

    # Save for graph
    daily_totals.append((d, daily_total))

    # 👉 NEW: collect data for pivot
    temp_df = merged[["product", "total_count_pct"]].copy()
    temp_df["date"] = d
    all_pct_data.append(temp_df)

# -------------------------------
# 📊 Generate graph
# -------------------------------

df_totals = pd.DataFrame(daily_totals, columns=["date", "total"])

df_totals["date_dt"] = df_totals["date"].apply(
    lambda x: datetime.strptime(x, "%d%b")
)
df_totals.sort_values("date_dt", inplace=True)

plt.figure(figsize=(10, 5))
plt.plot(df_totals["date"], df_totals["total"], marker='o')

plt.title("Total Product Count per Day")
plt.xlabel("Date")
plt.ylabel("Total Count")
plt.xticks(rotation=45)

plt.tight_layout()

graph_file = os.path.join(OUTPUT_DIR, "daily_totals.png")
plt.savefig(graph_file)
plt.show()

print(f"Graph saved to: {graph_file}")

# -------------------------------
# 📊 NEW: Pivot Table Generation
# -------------------------------

if all_pct_data:
    combined_pct_df = pd.concat(all_pct_data)

    pivot_df = combined_pct_df.pivot_table(
        index="product",
        columns="date",
        values="total_count_pct",
        fill_value=0
    )

    # Optional: sort columns by actual date
    sorted_dates = sorted(
        pivot_df.columns,
        key=lambda x: datetime.strptime(x, "%d%b")
    )
    pivot_df = pivot_df[sorted_dates]

    pivot_file = os.path.join(OUTPUT_DIR, "product_pct_pivot.csv")
    pivot_df.to_csv(pivot_file)

    print(f"Pivot table saved to: {pivot_file}")
