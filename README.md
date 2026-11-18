
# Local LLM Throughput Under Memory Pressure

## Project Overview
This project tests how different RAM limits affect the speed of a local AI model. We use Docker to control memory and llama.cpp to run the model.

## Tools Used
- GitHub Actions
- Docker
- Python
- llama.cpp
- TinyLlama 1.1B (GGUF)
- Matplotlib

## Environment Setup
The tests run on GitHub Actions using Ubuntu 24.04.

We use Docker to test four memory limits:
- 4 GB
- 2 GB
- 1 GB
- 512 MB

Each memory limit is tested three times using the same prompt and four CPU threads.

## Running the Tests
1. Open the GitHub repository.
2. Click **Actions**.
3. Select **Test RAM**.
4. Click **Run workflow**.
5. Wait for the tests to finish.
6. Download the `ram-test-results` artifact.

The workflow automatically runs the model, collects results, creates a CSV file, and generates graphs.

## Test Results

| RAM Limit | Average Generation Speed |
|---|---|
| 4 GB | 33.2 tokens/sec |
| 2 GB | 34.0 tokens/sec |
| 1 GB | 34.1 tokens/sec |
| 512 MB | 3.3 tokens/sec |

## Memory and Swap Usage
- At 1 GB, peak RAM usage was about 735 MB with no swap usage.
- At 512 MB, RAM reached its limit and swap usage was about 287 MB.
- The 512 MB tests were much slower because the system needed swap memory.

Memory and swap measurements were collected for the 1 GB and 512 MB tests.

## Results Files
- `results.csv` contains the test measurements.
- `results/` contains the individual test logs.
- `graphs/` contains the generated graphs.

These files are available in the GitHub Actions artifact after each successful run.

## Conclusion
The model performed at similar speeds with 4 GB, 2 GB, and 1 GB of RAM. When RAM was reduced to 512 MB, generation speed dropped significantly and swap usage increased.

This shows how limited memory can affect local AI model performance.

## Team Responsibilities
- **Brenda:** Environment setup, AI model, Docker, and memory testing.
- **Cameron:** Python development and interactive demo.
- **Begeline:** Testing, analysis, and final report.

## Test Results and Analysis

We tested the TinyLlama AI model using four different RAM limits: 4 GB, 2 GB, 1 GB, and 512 MB. Each test was repeated three times.

| RAM Limit | Average Generation Speed | Status |
|-----------|--------------------------|--------|
| 4 GB | 33.2 tokens/sec | Passed |
| 2 GB | 34.0 tokens/sec | Passed |
| 1 GB | 34.1 tokens/sec | Passed |
| 512 MB | 3.3 tokens/sec | Passed |

### What We Found

The model ran at almost the same speed with 4 GB, 2 GB, and 1 GB of RAM.

When we lowered RAM to 512 MB, the model became about 90% slower. It also started using swap memory because there was not enough RAM available.

All 12 tests finished successfully, but the results show that having too little RAM can make an AI model run much slower.

### Conclusion

Our results show that memory limits can affect how fast a local AI model runs. The biggest performance drop happened at 512 MB, where the system had to use swap memory.
