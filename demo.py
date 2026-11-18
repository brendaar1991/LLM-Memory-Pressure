
import os
import subprocess

# Our RAM options
a = {
    "1": ("4 GB", "4g"),
    "2": ("2 GB", "2g"),
    "3": ("1 GB", "1g"),
    "4": ("512 MB", "512m")
}

# Show the menu
def menu():
    print("\nLOCAL LLM MEMORY TEST")
    print("1. Test with 4 GB RAM")
    print("2. Test with 2 GB RAM")
    print("3. Test with 1 GB RAM")
    print("4. Test with 512 MB RAM")
    print("5. View saved results")
    print("6. View graphs")
    print("7. Exit")

# Run the model with Docker
def test(x):
    name, ram = a[x]

    print(f"\nRunning TinyLlama with {name} RAM...")

    # Give 512 MB extra swap
    swap = "1g" if ram == "512m" else ram

    # Use the current repo folder
    path = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(path, "results"), exist_ok=True)

    cmd = [
        "docker", "run", "--rm",
        f"--memory={ram}",
        f"--memory-swap={swap}",
        "--cpus=4",
        "-v", f"{path}:/work",
        "-w", "/work",
        "ubuntu:24.04",
        "bash", "-c",
        "export LD_LIBRARY_PATH=/work/llama.cpp/build/bin:$LD_LIBRARY_PATH; "
        "./llama.cpp/build/bin/llama-cli "
        "-m models/tinyllama.gguf "
        '-p "Explain artificial intelligence in simple words." '
        "-n 100 -t 4 --no-display-prompt"
    ]

    try:
        b = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300
        )

        f = os.path.join(path, "results", f"demo_{ram}.txt")
        with open(f, "w") as z:
            z.write(b.stdout)
            z.write(b.stderr)
            z.write(f"\nExit code: {b.returncode}\n")

        print(f"Test finished. Exit code: {b.returncode}")
        print(f"Results saved to results/demo_{ram}.txt")

    except subprocess.TimeoutExpired:
        print("Test stopped after 5 minutes.")

# Show saved results
def results():
    path = os.path.dirname(os.path.abspath(__file__))
    f = os.path.join(path, "results.csv")

    if not os.path.exists(f):
        print("No results.csv found. Download it from GitHub Actions.")
        return

    with open(f) as x:
        print("\n" + x.read())

# Show graph files
def graphs():
    path = os.path.dirname(os.path.abspath(__file__))
    f = os.path.join(path, "graphs")

    if not os.path.isdir(f):
        print("No graphs found. Download them from GitHub Actions.")
        return

    for x in sorted(os.listdir(f)):
        if x.endswith(".png"):
            print(x)

# Start the menu
while True:
    menu()
    x = input("\nChoose an option (1-7): ")

    if x in a:
        test(x)
    elif x == "5":
        results()
    elif x == "6":
        graphs()
    elif x == "7":
        print("Goodbye!")
        break
    else:
        print("Invalid option. Try again.")
