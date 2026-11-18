
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import subprocess
import shutil
import time

st.set_page_config(
    page_title="LLM Memory Pressure Dashboard",
    page_icon="🧠",
    layout="wide"
)

p = Path(__file__).parent
f = p / "results.csv"
g = p / "graphs"

st.title("🧠 LLM Memory Pressure Dashboard")
st.caption("TinyLlama 1.1B | llama.cpp | Docker Memory Testing")

if not f.exists():
    st.error("results.csv is missing.")
    st.stop()

df = pd.read_csv(f)

# clean up the results
for x in ["RAM_GB", "Prompt_tps", "Generation_tps",
          "RAM_Peak_MB", "Swap_Peak_MB", "Process_Peak_MB"]:
    df[x] = pd.to_numeric(df[x], errors="coerce")

df["RAM_Label"] = df["RAM_GB"].map({
    4.0: "4 GB",
    2.0: "2 GB",
    1.0: "1 GB",
    0.5: "512 MB"
})

order = ["4 GB", "2 GB", "1 GB", "512 MB"]

# navigation
page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Overview",
        "📊 Performance",
        "🧠 Memory Usage",
        "🔍 Compare Tests",
        "🧪 Test Simulator",
        "🚀 Live Testing",
        "📁 All Results"
    ]
)

st.sidebar.divider()
st.sidebar.write("**Project:** Local LLM Throughput Under Memory Pressure")
st.sidebar.write("**Model:** TinyLlama 1.1B")
st.sidebar.write("**Framework:** llama.cpp")

# choose memory
ram = st.sidebar.selectbox("RAM Limit", order)

a = df[df["RAM_Label"] == ram].copy()

def chart(data, x, y, title, color=None):
    z = px.bar(
        data,
        x=x,
        y=y,
        color=color,
        title=title,
        text_auto=".1f"
    )
    z.update_layout(
        height=430,
        xaxis_title=None,
        yaxis_title="Tokens per second"
    )
    st.plotly_chart(z, use_container_width=True)

def metrics(data):
    x, y, z = st.columns(3)

    x.metric(
        "Generation Speed",
        f"{data['Generation_tps'].mean():.1f} t/s"
    )

    y.metric(
        "Prompt Speed",
        f"{data['Prompt_tps'].mean():.1f} t/s"
    )

    z.metric(
        "Tests Passed",
        f"{(data['Status'] == 'Passed').sum()}/{len(data)}"
    )

# average results
avg = df.groupby("RAM_Label", as_index=False).agg({
    "Generation_tps": "mean",
    "Prompt_tps": "mean"
})

avg["RAM_Label"] = pd.Categorical(
    avg["RAM_Label"],
    categories=order,
    ordered=True
)

avg = avg.sort_values("RAM_Label")

if page == "🏠 Overview":

    st.header("Project Overview")

    st.write(
        "This project tests how limiting RAM affects the "
        "performance of a local AI language model."
    )

    x, y, z = st.columns(3)

    x.metric("Total Tests", len(df))
    y.metric("RAM Configurations", df["RAM_GB"].nunique())
    z.metric("Successful Tests", (df["Status"] == "Passed").sum())

    st.divider()

    st.subheader(f"Selected RAM: {ram}")
    metrics(a)

    chart(
        avg,
        "RAM_Label",
        "Generation_tps",
        "Average Generation Speed"
    )

    if len(avg) == 4:
        x = avg.loc[avg["RAM_Label"] == "1 GB", "Generation_tps"].iloc[0]
        y = avg.loc[avg["RAM_Label"] == "512 MB", "Generation_tps"].iloc[0]

        if x > 0:
            drop = (x - y) / x * 100
            st.warning(
                f"At 512 MB, generation speed dropped "
                f"{drop:.1f}% compared with 1 GB."
            )

    st.subheader("Project Findings")

    st.write(
        "The model performed at almost the same speed with "
        "4 GB, 2 GB, and 1 GB of RAM. At 512 MB, performance "
        "dropped significantly and the system used swap memory."
    )

elif page == "📊 Performance":

    st.header("Performance Analysis")

    metric = st.selectbox(
        "Choose performance measurement",
        ["Generation_tps", "Prompt_tps"]
    )

    kind = st.radio(
        "Chart Type",
        ["Bar Chart", "Line Chart", "Scatter Plot"],
        horizontal=True
    )

    if kind == "Bar Chart":
        chart(avg, "RAM_Label", metric, metric)

    elif kind == "Line Chart":
        z = px.line(
            avg,
            x="RAM_Label",
            y=metric,
            markers=True,
            title=metric
        )
        st.plotly_chart(z, use_container_width=True)

    else:
        z = px.scatter(
            df,
            x="RAM_Label",
            y=metric,
            color="Test",
            hover_data=["Status"],
            title="Individual Test Performance"
        )
        st.plotly_chart(z, use_container_width=True)

    st.subheader("Individual Runs")

    z = px.line(
        df,
        x="Test",
        y=metric,
        color="RAM_Label",
        markers=True,
        category_orders={"RAM_Label": order}
    )

    st.plotly_chart(z, use_container_width=True)

    st.subheader("Performance Statistics")

    st.dataframe(
        df.groupby("RAM_Label", observed=True)[metric]
        .agg(["mean", "min", "max", "std"])
        .round(2),
        use_container_width=True
    )

elif page == "🧠 Memory Usage":

    st.header("Memory and Swap Usage")

    st.info(
        "Memory measurements were recorded for 1 GB and "
        "512 MB tests. The 2 GB and 4 GB memory fields "
        "were not recorded."
    )

    cols = [
        "RAM_Peak_MB",
        "Swap_Peak_MB",
        "Process_Peak_MB"
    ]

    b = df.dropna(subset=["RAM_Peak_MB"]).copy()

    if not b.empty:

        x = st.selectbox("Choose measurement", cols)

        z = px.bar(
            b,
            x="RAM_Label",
            y=x,
            color="Test",
            barmode="group",
            title=x.replace("_", " ")
        )

        st.plotly_chart(z, use_container_width=True)

        st.subheader("Memory Measurements")

        st.dataframe(
            b[["RAM_Label", "Test"] + cols],
            use_container_width=True,
            hide_index=True
        )

        st.subheader("RAM vs Swap")

        z = b.groupby("RAM_Label", as_index=False)[
            ["RAM_Peak_MB", "Swap_Peak_MB"]
        ].mean()

        st.bar_chart(
            z.set_index("RAM_Label")
        )

elif page == "🔍 Compare Tests":

    st.header("Compare RAM Configurations")

    x = st.selectbox("First RAM Limit", order, index=2)
    y = st.selectbox("Second RAM Limit", order, index=3)

    a1 = df[df["RAM_Label"] == x]
    a2 = df[df["RAM_Label"] == y]

    c, d = st.columns(2)

    with c:
        st.subheader(x)
        metrics(a1)

    with d:
        st.subheader(y)
        metrics(a2)

    v1 = a1["Generation_tps"].mean()
    v2 = a2["Generation_tps"].mean()

    if v1 > 0:
        change = (v2 - v1) / v1 * 100

        st.metric(
            "Generation Speed Change",
            f"{change:+.1f}%"
        )

    z = pd.DataFrame({
        "RAM": [x, y],
        "Generation Speed": [v1, v2],
        "Prompt Speed": [
            a1["Prompt_tps"].mean(),
            a2["Prompt_tps"].mean()
        ]
    })

    st.bar_chart(
        z.set_index("RAM")
    )

elif page == "🧪 Test Simulator":

    st.header("Interactive Performance Simulator")

    st.write(
        "Explore estimated performance based on our "
        "saved experiment results. This does not run the model."
    )

    x = st.select_slider(
        "Choose RAM",
        options=[0.5, 1, 2, 4],
        value=1,
        format_func=lambda v: "512 MB" if v == 0.5 else f"{v:g} GB"
    )

    y = df[df["RAM_GB"] == x]

    if st.button("▶ Simulate Test", type="primary"):

        bar = st.progress(0, text="Loading saved measurements...")

        for i in range(101):
            bar.progress(i, text=f"Simulating... {i}%")
            time.sleep(0.005)

        st.success("Simulation completed!")

        metrics(y)

        st.subheader("Simulated Results From Saved Tests")

        st.dataframe(
            y,
            use_container_width=True,
            hide_index=True
        )

        if x == 0.5:
            st.warning(
                "At 512 MB, the model was much slower "
                "and used swap memory."
            )

elif page == "🚀 Live Testing":

    st.header("Live Docker Testing")

    st.write(
        "Run a real experiment using the existing "
        "project workflow."
    )

    st.warning(
        "Live tests need Docker, the model files, "
        "and the correct llama.cpp command. "
        "The dashboard will not run a test until "
        "the project runner is connected."
    )

    x = st.selectbox("RAM Limit for Live Test", order)

    st.write("Docker installed:", "Yes" if shutil.which("docker") else "No")

    if st.button("▶ Check Docker"):

        if shutil.which("docker"):
            try:
                z = subprocess.run(
                    ["docker", "info"],
                    capture_output=True,
                    text=True,
                    timeout=15
                )

                if z.returncode == 0:
                    st.success("Docker is ready.")
                else:
                    st.error("Docker is installed but not available.")

            except Exception as e:
                st.error(str(e))
        else:
            st.error("Docker is not installed in this environment.")

    st.info(
        "The real Run Test button will be connected "
        "to the project's existing test script."
    )

elif page == "📁 All Results":

    st.header("All Experiment Results")

    x = st.multiselect(
        "Filter RAM Limits",
        order,
        default=order
    )

    y = df[df["RAM_Label"].isin(x)]

    st.dataframe(
        y,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "⬇ Download Filtered Results",
        data=y.to_csv(index=False),
        file_name="filtered_results.csv",
        mime="text/csv"
    )

    st.subheader("Saved Project Graphs")

    if g.exists():
        files = sorted(g.glob("*.png"))

        if files:
            x = st.selectbox(
                "Choose a Graph",
                files,
                format_func=lambda v: v.stem.replace("_", " ").title()
            )

            st.image(str(x), use_container_width=True)

            st.download_button(
                "⬇ Download Graph",
                data=x.read_bytes(),
                file_name=x.name,
                mime="image/png"
            )
        else:
            st.info("No graph images found.")
    else:
        st.info("The graphs folder was not found.")
