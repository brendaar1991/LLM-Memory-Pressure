
import pandas as pd
import matplotlib.pyplot as plt
import os

# Read our test results
df = pd.read_csv("results.csv")

# Only use tests that passed
df = df[df["Status"] == "Passed"].copy()

# Make sure our numbers are numbers
for c in ["RAM_GB", "Test", "Prompt_tps", "Generation_tps"]:
    df[c] = pd.to_numeric(df[c])

# Make a folder for the graphs
os.makedirs("graphs", exist_ok=True)

# Graph 1 - Generation speed for each test
a = df.pivot(index="Test", columns="RAM_GB", values="Generation_tps")
a.plot(kind="bar", figsize=(9, 5))
plt.title("Generation Speed by RAM Limit")
plt.xlabel("Test Number")
plt.ylabel("Tokens per Second")
plt.legend(title="RAM (GB)")
plt.tight_layout()
plt.savefig("graphs/generation_speed.png", dpi=200)
plt.close()

# Graph 2 - Prompt speed for each test
b = df.pivot(index="Test", columns="RAM_GB", values="Prompt_tps")
b.plot(kind="bar", figsize=(9, 5))
plt.title("Prompt Speed by RAM Limit")
plt.xlabel("Test Number")
plt.ylabel("Tokens per Second")
plt.legend(title="RAM (GB)")
plt.tight_layout()
plt.savefig("graphs/prompt_speed.png", dpi=200)
plt.close()

# Graph 3 - Average performance
c = df.groupby("RAM_GB")[["Prompt_tps", "Generation_tps"]].mean()
c.plot(kind="bar", figsize=(9, 5))
plt.title("Average Performance by RAM Limit")
plt.xlabel("RAM Limit (GB)")
plt.ylabel("Average Tokens per Second")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("graphs/average_performance.png", dpi=200)
plt.close()

# Graph 4 - Performance consistency
d = df.pivot(index="Test", columns="RAM_GB", values="Generation_tps")
d.plot(kind="line", marker="o", figsize=(9, 5))
plt.title("Generation Speed Across Tests")
plt.xlabel("Test Number")
plt.ylabel("Tokens per Second")
plt.xticks([1, 2, 3])
plt.legend(title="RAM (GB)")
plt.tight_layout()
plt.savefig("graphs/performance_consistency.png", dpi=200)
plt.close()

print("All 4 graphs saved!")
