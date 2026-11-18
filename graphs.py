
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Get our test results
a = pd.read_csv("results.csv")
os.makedirs("graphs", exist_ok=True)

# Only use tests that passed
b = a[a["Status"] == "Passed"].copy()

for x in ["RAM_GB", "Test", "Prompt_tps", "Generation_tps"]:
    b[x] = pd.to_numeric(b[x], errors="coerce")

b = b.dropna(subset=["RAM_GB", "Test"])

# Graph 1 - Generation speed
c = b.pivot(index="Test", columns="RAM_GB", values="Generation_tps")
c.plot(kind="bar", figsize=(9, 5))
plt.title("Generation Speed by RAM Limit")
plt.xlabel("Test Number")
plt.ylabel("Tokens per Second")
plt.legend(title="RAM (GB)")
plt.tight_layout()
plt.savefig("graphs/generation_speed.png", dpi=200)
plt.close()

# Graph 2 - Prompt speed
d = b.pivot(index="Test", columns="RAM_GB", values="Prompt_tps")
d.plot(kind="bar", figsize=(9, 5))
plt.title("Prompt Speed by RAM Limit")
plt.xlabel("Test Number")
plt.ylabel("Tokens per Second")
plt.legend(title="RAM (GB)")
plt.tight_layout()
plt.savefig("graphs/prompt_speed.png", dpi=200)
plt.close()

# Graph 3 - Average performance
e = b.groupby("RAM_GB")[["Prompt_tps", "Generation_tps"]].mean()
e.plot(kind="bar", figsize=(9, 5))
plt.title("Average Performance by RAM Limit")
plt.xlabel("RAM (GB)")
plt.ylabel("Average Tokens per Second")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("graphs/average_performance.png", dpi=200)
plt.close()

# Graph 4 - Performance consistency
c.plot(kind="line", marker="o", figsize=(9, 5))
plt.title("Generation Speed Across Tests")
plt.xlabel("Test Number")
plt.ylabel("Tokens per Second")
plt.xticks([1, 2, 3])
plt.legend(title="RAM (GB)")
plt.tight_layout()
plt.savefig("graphs/performance_consistency.png", dpi=200)
plt.close()

# Graph 5 - RAM usage
if "RAM_Peak_MB" in b.columns:
    f = b.groupby("RAM_GB")["RAM_Peak_MB"].mean()
    f.dropna().plot(kind="bar", figsize=(9, 5))
    plt.title("Peak RAM Usage by RAM Limit")
    plt.xlabel("RAM (GB)")
    plt.ylabel("Peak RAM (MB)")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig("graphs/ram_usage.png", dpi=200)
    plt.close()

# Graph 6 - Swap usage
if "Swap_Peak_MB" in b.columns:
    g = b.groupby("RAM_GB")["Swap_Peak_MB"].mean()
    g.dropna().plot(kind="bar", figsize=(9, 5))
    plt.title("Peak Swap Usage by RAM Limit")
    plt.xlabel("RAM (GB)")
    plt.ylabel("Peak Swap (MB)")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig("graphs/swap_usage.png", dpi=200)
    plt.close()

print("Graphs saved in graphs/ folder!")

