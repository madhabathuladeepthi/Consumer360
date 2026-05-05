# ================================
# Consumer360 Analytics Engine
# ================================

import pandas as pd
from sqlalchemy import create_engine
from mlxtend.frequent_patterns import apriori, association_rules
from scipy.stats import f_oneway

# --------------------------------
# 1️⃣ Connect to PostgreSQL
# --------------------------------

username = "postgres"
password = "admin123"
host = "localhost"
port = "5432"
database = "consumer360"

engine = create_engine(
    f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
)

print("Connected to PostgreSQL")

# --------------------------------
# 2️⃣ Pull Customer Data
# --------------------------------

query = "SELECT * FROM single_customer_view;"
rfm_df = pd.read_sql(query, engine)

print("Customer records loaded:", len(rfm_df))

# --------------------------------
# 3️⃣ Calculate RFM Scores
# --------------------------------

rfm_df['R_Score'] = pd.qcut(rfm_df['recency_days'], q=5, duplicates='drop').cat.codes + 1
rfm_df['F_Score'] = pd.qcut(rfm_df['frequency'], q=5, duplicates='drop').cat.codes + 1
rfm_df['M_Score'] = pd.qcut(rfm_df['monetary'], q=5, duplicates='drop').cat.codes + 1

rfm_df['R_Score'] = rfm_df['R_Score'].astype(int)
rfm_df['F_Score'] = rfm_df['F_Score'].astype(int)
rfm_df['M_Score'] = rfm_df['M_Score'].astype(int)

rfm_df['RFM_Score'] = (
    rfm_df['R_Score'] +
    rfm_df['F_Score'] +
    rfm_df['M_Score']
)

print("RFM scores calculated")

# --------------------------------
# 4️⃣ Customer Segmentation
# --------------------------------

def segment_customer(score):

    if score >= 13:
        return "Champions"

    elif score >= 10:
        return "Loyalists"

    elif score >= 7:
        return "Potential Loyalist"

    elif score >= 5:
        return "At Risk"

    else:
        return "Hibernating"


rfm_df["Segment"] = rfm_df["RFM_Score"].apply(segment_customer)

print("\nCustomer Segment Distribution:\n")
print(rfm_df["Segment"].value_counts())

# --------------------------------
# 5️⃣ Statistical Validation
# --------------------------------

print("\nAverage Spend per Segment:\n")

segment_summary = rfm_df.groupby("Segment").agg({
    "monetary":"mean",
    "frequency":"mean",
    "recency_days":"mean"
}).sort_values(by="monetary", ascending=False)

print(segment_summary)

# ANOVA Test

groups = [
    group["monetary"].values
    for name, group in rfm_df.groupby("Segment")
]

f_stat, p_value = f_oneway(*groups)

print("\nANOVA Statistical Test")
print("F-statistic:", f_stat)
print("p-value:", p_value)

if p_value < 0.05:
    print("Segments are statistically different")
else:
    print("No statistical difference found")

# --------------------------------
# 6️⃣ Market Basket Analysis
# --------------------------------

print("\nRunning Market Basket Analysis...")

basket_query = """
SELECT invoiceno, stockcode
FROM fact_sales
"""

basket_df = pd.read_sql(basket_query, engine)

print("Basket dataframe columns:")
print(basket_df.columns)

basket = basket_df.groupby(["invoiceno","stockcode"])["stockcode"]\
            .count().unstack().fillna(0)

basket = (basket > 0).astype(int)

frequent_items = apriori(basket, min_support=0.02, use_colnames=True)

rules = association_rules(
    frequent_items,
    metric="lift",
    min_threshold=1.2
)

print("\nTop Product Associations:\n")

print(
    rules[["antecedents","consequents","support","confidence","lift"]]
    .sort_values(by="lift", ascending=False)
    .head(10)
)

print("\nConsumer360 Analysis Completed Successfully")
