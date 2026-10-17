
"""Task 11 — Two visualizations (analysis/visualize.py) — 3 marks
Using Matplotlib, save two PNGs to visualizations/:

return_rate_by_payment.png — a bar chart of return rate by (cleaned) payment_method, descending, with the exact percentage labeled on each bar, and a title that states the finding (e.g. "COD Returns at 44.4% — 3x Card").
monthly_revenue_trend.png — a line chart of the outlier-corrected monthly revenue from Task 10 (not the outlier-inflated version), with axis labels and a title naming the actual peak month.
Both scripts must be re-runnable end-to-end (python analysis/clean_and_eda.py then python analysis/visualize.py) and regenerate identical numbers/files from the raw CSVs every time — no manual editing of intermediate output.
"""



return_rate_by_payment = merged.groupby(('payment_method'))['returned'].agg(returns = 'mean')
return_rate_by_payment_chart = return_rate_by_payment['returns'].round(2)*100
sales_without_outlier
return_rate_by_payment_chart

"""return_rate_by_payment.png

"""

# return_rate_by_payment_chart.plot(kind='bar', x='returns', color='skyblue')
# return_rate_by_payment_chart.set_index('returns', inplace=True)
import os
os.makedirs("visualizations", exist_ok=True)
fig, ax = plt.subplots(figsize=(7, 5))
bars = ax.bar(return_rate_by_payment_chart.index, return_rate_by_payment_chart.values, color=["#c0392b" if m == "COD" else "#7f8c8d" for m in return_rate_by_payment_chart.index])
for bar, value in zip(bars, return_rate_by_payment_chart.values):
    ax.text(bar.get_x() + bar.get_width() / 2, value + 0.8, f"{value:.1f}%", ha="center", fontweight="bold")

ax.set_title(f"COD Returns at {return_rate_by_payment_chart['COD']:.1f}% \u2014 {return_rate_by_payment_chart['COD'] / return_rate_by_payment_chart['CARD']:.0f}x Card", fontweight="bold")
ax.set_xlabel("Payment method (cleaned)")
ax.set_ylabel("Return rate (%)")
fig.tight_layout()
fig.savefig("visualizations/return_rate_by_payment.png", dpi=150)
plt.show()

merged.head(2)



# df["ym"] = pd.to_datetime(df["order_date"]).dt.to_period("M").astype(str)
monthly = merged[~merged.outlier].groupby("month")["order_value"].sum().round(2)
peak = monthly.idxmax()
peak_name = pd.Period(peak).strftime("%B")
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(monthly.index, monthly.values, marker="o", linewidth=2, color="#2c7fb8")
ax.scatter([peak], [monthly[peak]], s=140, color="#c0392b", zorder=3)
ax.annotate(f"{peak_name} peak\n\u20b9{monthly[peak]:,.2f}", (peak, monthly[peak]),
            textcoords="offset points", xytext=(0, 12), ha="center", fontweight="bold")
ax.set_title(f"Outlier-Corrected Monthly Revenue \u2014 {peak_name} Is the True Peak",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Month (2026)")
ax.set_ylabel("Revenue (INR)")
ax.set_ylim(0, monthly.max() * 1.2)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig("visualizations/monthly_revenue_trend.png", dpi=150)
plt.show()      # <- shows the graph in the notebook
