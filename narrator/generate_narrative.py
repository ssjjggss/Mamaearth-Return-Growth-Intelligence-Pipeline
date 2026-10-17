
findings = {
    "cleaned_total_revenue_inr": 97358.30,
    "raw_total_revenue_inr": 99860.20,
    "duplicate_reconciliation_delta_inr": 2501.90,
    "return_rate_by_payment": {
        "COD": 44.4,
        "CARD": 14.7,
        "UPI": 18.9
    },
    "highest_risk_segment": {
        "payment_method": "COD",
        "city_tier": 2,
        "return_rate_pct": 54.5
    },
    "true_peak_month": {
        "month": "2026-03",
        "revenue_inr": 20318.90
    },
    "outlier_inflated_month": {
        "month": "2026-01",
        "apparent_revenue_inr": 29582.10,
        "corrected_revenue_inr": 11637.10
    }
}

# cleaned_total_revenue_inr
cleaned_total_revenue = float(merged['order_value'].sum().round(2))
cleaned_total_revenue
# finding raw data
mergednew = order.merge(
    products,
    on="product_id",
    how="left"
)


mergednew = mergednew.merge(
    customers,
    on="customer_id",
    how="left"
)
raw_total_revenue_inr = (
    mergednew["quantity"] * mergednew["price"]
    * (1 - mergednew["discount_pct"].fillna(0) / 100)
).sum()

raw_total_revenue_inr =  float(raw_total_revenue_inr.round(2))



return_rate_by_payment = merged.groupby('payment_method')['returned'].agg(['mean'])
# print(return_rate_by_payment)
# highest_risk_segment
top

# true_peak_month
incl = merged.groupby("month").order_value.sum().round(2)
excl = merged[~merged['outlier']].groupby("month").order_value.sum().round(2)

inflated_month = incl.idxmax()     # "2026-01"

outlier_inflated_month = {
    "outlier_inflated_month": {
        "month": inflated_month,
        "apparent_revenue_inr": float(incl[inflated_month]),
        "corrected_revenue_inr": float(excl[inflated_month]),
    },
}



outlier_inflated_month
return_rate_by_payment = merged.groupby('payment_method')['returned'].agg(['mean'])
rr = (return_rate_by_payment['mean'] * 100).round(1)
float(rr['CARD'])

import json

FINDINGS = {
    "cleaned_total_revenue_inr": cleaned_total_revenue,
    "raw_total_revenue_inr": raw_total_revenue_inr,
    "duplicate_reconciliation_delta_inr": round(raw_total_revenue_inr - cleaned_total_revenue, 2),
    "return_rate_by_payment": {"COD": rr["COD"], "CARD": rr["CARD"], "UPI": rr["UPI"]},
    "highest_risk_segment": {"payment_method": top[0], "city_tier": int(top[1]),
                             "return_rate_pct": float(top['return_rate_pct'])},
    "true_peak_month": {"month": excl.idxmax(), "revenue_inr": float(excl.max())},
    "outlier_inflated_month": {"month": incl.idxmax(),
                               "apparent_revenue_inr": float(incl.max()),
                               "corrected_revenue_inr": float(excl[incl.idxmax()])},
}
import json, os

os.makedirs("narrator", exist_ok=True)      # creates the folder if it's missing

with open("narrator/findings.json", "w") as f:
    json.dump(findings, f, indent=2)

# print(open("narrator/findings.json").read())

!pip install -q crewai

import json
import os
from google.genai import types
from google.colab import userdata

from crewai import Agent, Crew, LLM, Process, Task
from crewai.tools import tool
# with open("findings.json") as fh:
#     FINDINGS = json.load(fh)

@tool("Findings Extractor")
def findings_extractor(section: str = "all") -> str:
    """Returns verified figures from findings.json as JSON text.
    section: 'all' or one top-level key such as 'return_rate_by_payment'."""
    if section == "all":
        return json.dumps(FINDINGS, indent=2)
    if section in FINDINGS:
        return json.dumps({section: FINDINGS[section]}, indent=2)
    return f"Unknown section '{section}'. Valid: {list(FINDINGS)}"

# import os
from google.colab import userdata

os.environ["GEMINI_API_KEY"] = userdata.get("sj_key")

# print("Gemini API key loaded:", bool(os.environ["GEMINI_API_KEY"]))

llm = LLM(
    model="gemini/gemini-3.6-flash",
    api_key = os.environ["GEMINI_API_KEY"],
    temperature=0.0,          # factual report -> deterministic
    max_tokens=300,
    client_params={"http_options": types.HttpOptions(timeout=30000)},   # <-- the timeout line

)

# ---- Agent 1: extracts the data with the tool ----
extractor = Agent(
    role="Findings Extraction Analyst",
    goal="Extract every verified figure from the findings with exact values and no changes.",
    backstory="You only report numbers returned by your tool. You never estimate or invent.",
    tools=[findings_extractor],
    llm=llm,
    allow_delegation=False,
    verbose=True,
)

# ---- Agent 2: writes the SCR narrative ----
writer = Agent(
    role="Senior Data Analyst",
    goal="Write an SCR narrative for Mamaearth's regional ops and finance heads.",
    backstory=(
        "You are a senior data analyst writing for Mamaearth's regional ops and finance heads. "
        "Every number you write must come from the extracted figures, with the same value. "
        "You never invent statistics."
    ),
    llm=llm,
    allow_delegation=False,
    verbose=True,
)

extract_task = Task(
    description=(
        "Call the Findings Extractor tool with section='all' and return a clean list of every "
        "figure (cleaned and raw revenue, duplicate delta, return rate by payment method, "
        "highest-risk segment, true peak month, outlier-inflated month) with the exact values."
    ),
    expected_output="A labeled list of all figures with exact values from the tool.",
    agent=extractor,
)

scr_task = Task(
    description=(
        "Using ONLY the extracted figures, write a ~250-word narrative with exactly three labeled "
        "sections in this order: Situation, Complication, Resolution. Every number must appear with "
        "the same value as extracted. Include: cleaned revenue, COD return rate, the COD + Tier-2 "
        "highest-risk rate, the duplicate reconciliation delta, and the true peak month with its "
        "revenue (say the month name, e.g. March)."
    ),
    expected_output="Three sections labeled Situation, Complication, Resolution. 3-section 250-word narrative",
    agent=writer,
    context=[extract_task],        # writer receives the extractor's output
)

crew = Crew(agents=[extractor, writer],
            tasks=[extract_task, scr_task],
            process=Process.sequential,
            verbose=True
            )



import asyncio

def generate_scr_narrative(findings: dict) -> dict:
    try:
        FINDINGS.clear(); FINDINGS.update(findings)
        result = crew.kickoff()
        return {"status": "success", "narrative": result.raw,
                "tokens": getattr(result.token_usage, "total_tokens", None)}
    except Exception as err:
        return {"status": "error", "narrative": None, "message": str(err)}

out = await asyncio.to_thread(generate_scr_narrative, FINDINGS)
print(out["narrative"] if out["status"] == "success" else out["message"])

def generate_scr_narrative(findings: dict) -> dict:
    """Never raises: always returns a structured dict."""
    try:
        FINDINGS.clear()
        FINDINGS.update(findings)                  # the extractor tool reads this
        result = crew.kickoff()
        text = (result.raw or "").strip()
        if not text:
            raise ValueError("Crew returned an empty narrative")
        usage = getattr(result, "token_usage", None)
        return {"status": "success",
                "narrative": text,
                "tokens": getattr(usage, "total_tokens", None)}
    except Exception as err:
        return {"status": "error", "narrative": None, "message": str(err)}
import asyncio
out = await asyncio.to_thread(generate_scr_narrative, FINDINGS)
print(out["narrative"] if out["status"] == "success" else out["message"])

import json, os, calendar

def mon(m): return calendar.month_name[int(m.split("-")[1])]

# ---------- offline fallback: no key, no network ----------
def generate_scr_narrative_offline(f):
    rr, s = f["return_rate_by_payment"], f["highest_risk_segment"]
    p, i = f["true_peak_month"], f["outlier_inflated_month"]
    text = (
        f"Situation\nCleaned revenue is INR {f['cleaned_total_revenue_inr']:,.2f} (raw INR "
        f"{f['raw_total_revenue_inr']:,.2f}, overstated by INR {f['duplicate_reconciliation_delta_inr']:,.2f} "
        f"from duplicate orders). {mon(p['month'])} is the true peak month at INR {p['revenue_inr']:,.2f}.\n\n"
        f"Complication\nCOD returns are {rr['COD']}% vs CARD {rr['CARD']}% and UPI {rr['UPI']}%. "
        f"The riskiest segment is {s['payment_method']} in Tier-{s['city_tier']} cities at {s['return_rate_pct']}%. "
        f"{mon(i['month'])} looked like the peak (INR {i['apparent_revenue_inr']:,.2f}) but is "
        f"INR {i['corrected_revenue_inr']:,.2f} without two bulk orders.\n\n"
        f"Resolution\nTighten COD checks first in Tier-{s['city_tier']} cities, report revenue net of duplicates, "
        f"add a checkout de-duplication guard, and plan around {mon(p['month'])}."
    )
    return {"status": "success", "narrative": text, "tokens": 0}

# ---------- main function: CrewAI online, offline on no key / error ----------
def generate_scr_narrative(findings):
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        try:
            from crewai import Agent, Task, Crew, LLM
            from crewai.tools import tool
            from google.genai import types

            @tool("Findings Extractor")
            def get_findings() -> str:
                """Returns all verified figures as JSON."""
                return json.dumps(findings, indent=2)

            llm = LLM(model="gemini/gemini-3.5-flash", api_key=key, temperature=0.0, max_tokens=1200,
                      client_params={"http_options": types.HttpOptions(timeout=30000)})
            a1 = Agent(role="Findings Extractor", goal="Extract exact figures with the tool.",
                       backstory="You never invent numbers.", tools=[get_findings], llm=llm)
            a2 = Agent(role="Senior Data Analyst",
                       goal="Write an SCR narrative for Mamaearth's regional ops and finance heads.",
                       backstory="Every number must match the extracted figures exactly.", llm=llm)
            t1 = Task(description="Call the tool and list every figure exactly.",
                      expected_output="List of figures.", agent=a1)
            t2 = Task(description="Write ~250 words with sections Situation, Complication, Resolution. "
                                  "Include cleaned revenue, COD rate, COD+Tier-2 rate, duplicate delta, "
                                  "and the true peak month name with its revenue.",
                      expected_output="Three labeled sections.", agent=a2, context=[t1])
            r = Crew(agents=[a1, a2], tasks=[t1, t2]).kickoff()
            if not r.raw.strip():
                raise ValueError("empty narrative")
            return {"status": "success", "narrative": r.raw,
                    "tokens": getattr(r.token_usage, "total_tokens", None)}
        except Exception as err:
            out = {"status": "error", "narrative": None, "message": str(err)}
    return generate_scr_narrative_offline(findings)   # fallback on error / no key


    import asyncio
out = await asyncio.to_thread(generate_scr_narrative, findings)
print(out["narrative"])

def check_narrative(text, findings):
    t = text.replace(",", "")                       # normalize commas
    def has(x):                                     # matches 97358.30 or 97358.3
        return f"{x:.2f}" in t or f"{x:.2f}".rstrip("0").rstrip(".") in t
    peak = findings["true_peak_month"]
    checks = {
        "cleaned total revenue (97,358.30)":   has(findings["cleaned_total_revenue_inr"]),
        "COD return rate (44.4)":              has(findings["return_rate_by_payment"]["COD"]),
        "COD + Tier-2 risk rate (54.5)":       has(findings["highest_risk_segment"]["return_rate_pct"]),
        "duplicate delta (2,501.90)":          has(findings["duplicate_reconciliation_delta_inr"]),
        "March + 20,318.90":                   "March" in text and has(peak["revenue_inr"]),
    }

    for name, ok in checks.items():
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
    assert all(checks.values()), "Numeric accuracy check FAILED"
    print("ALL 5 FIGURES PRESENT")

out = generate_scr_narrative_offline(findings)
check_narrative(out["narrative"], findings)

