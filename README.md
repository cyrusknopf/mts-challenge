# ✨ PRISM Challenge ✨

```
 ________________
 /_______________/\
 \ \            / /
  \ \    ______/_/_______
   \ \  /\______________/\
 ___\ \_\_\__/ /_      / /
/\___\ \____/ /__\    / /
\ \   \ \ \ \/ / /   / /
 \ \   \ \/\ \/ /   / /
  \ \   \/_/\/ /   / /
   \ \      / /\  / /
    \ \    / /\ \/ /
     \ \  / /  \_\/
      \ \/ /
       \/_/
```

Welcome to the PRISM Challenge! This project provides the backend infrastructure for a sophisticated trading and portfolio management competition. Teams interact with an API to receive client contexts, design investment portfolios, and submit them for evaluation based on multiple financial metrics.

## 🏗️ Architecture Overview

The PRISM challenge runs as a multi-container application orchestrated using Docker Compose. The main components are:

1.  **`prism-server` (Go)**: The main API server that handles team requests (`/request`, `/submit`, `/info`), manages API keys, interacts with the database, and orchestrates portfolio evaluation.
2.  **`prism-llm` (Python/Hugging Face)**: An LLM server that generates client context narratives based on input data using models like Flan-T5.
3.  **`prism-evaluation` (Python)**: Scripts responsible for calculating portfolio scores based on various metrics like RoI, diversification, client satisfaction, and risk-adjusted returns.
4.  **`prism-website` (Next.js)**: A web application that displays the competition leaderboard by fetching data from the `prism-server`.
5.  **`postgresql` (Postgres)**: The database storing team information, scores, and submission timestamps.

## 🚀 Technologies Used

- **Backend**: Go, Python 🐍 (Requests, AIOHTTP, Pandas, NumPy, Faker)
- **Frontend**: Next.js (React), TypeScript, Tailwind CSS
- **Database**: PostgreSQL 🐘
- **AI/ML**: Hugging Face Transformers 🤗 (e.g., Flan-T5)
- **Containerization**: Docker 🐳, Docker Compose
- **External APIs**: Polygon.io (for financial data)

## 📋 Prerequisites

- Docker ([Install Guide](https://docs.docker.com/engine/install/))
- Docker Compose ([Install Guide](https://docs.docker.com/compose/install/))
- A Polygon.io API Key for fetching stock data.
- A `.env` file in the project root directory.

## 🛠️ Setup & Running

1.  **Clone the Repository**:
    ```bash
    git clone <your-repository-url>
    cd mts-challenge
    ```
2.  **Create `.env` file**:
    Create a file named `.env` in the root of the project and add your Polygon API key:
    ```env
    POLYGON_API_KEY=YOUR_POLYGON_API_KEY_HERE
    ```
    _Replace `YOUR_POLYGON_API_KEY_HERE` with your actual key._
3.  **Run with Docker Compose**:

    ```bash
    docker-compose up --build -d
    ```

    This command will build the necessary images and start all the services in detached mode.

4.  **Accessing Services**:
    - **Main API (`prism-server`)**: `http://localhost:8082`
    - **Leaderboard Website (`prism-website`)**: `http://localhost:80`
    - **LLM Server (`prism-llm`)**: Runs internally, accessible by `prism-server`.
    - **Database (`postgresql`)**: Runs internally, accessible by other services.

## 🎮 How to Participate / Usage

1.  **Obtain API Key**: Your team should receive an API key. For administrators, keys can be generated and added using the `prism-postgres_scripts/add_user.sh` script.
2.  **Interact with the API**: Use the API endpoints exposed by `prism-server` on port `8082`. You must include your API key in the `X-API-Code` header for all requests.
    - **GET `/request`**: Retrieves the client context (JSON format) including budget, investment period, client profile details, and any investment dislikes.
    - **POST `/submit`**: Submits your designed portfolio (JSON list of `{"ticker": "...", "quantity": ...}`) for evaluation.
    - **GET `/info`**: Fetches your team's current information (points, profit, last submission time).
3.  **Example Interaction**: See `starter.py` for a basic Python example of how to interact with the API.
4.  **Testing/Benchmarking**:
    - Use `benchmark.py` to test API latency.
    - Use `api_req.py` for more advanced API interaction testing, including sending multiple requests concurrently.

## 💯 Scoring

Your portfolio submissions are evaluated based on several factors:

- 📈 **Return on Investment (RoI)**: Profit relative to the initial budget.
- ⚖️ **Portfolio Diversification**: Considers the number of unique stocks, distribution of investment across stocks, and distribution across different industry sectors (using SIC codes).
- 😌 **Client Satisfaction**: Measures how well the portfolio's risk (standard deviation) aligns with the client's generated risk profile (based on age, employment, etc.).
- 📊 **Risk-Adjusted Returns**: Calculated using the Sharpe and Sortino ratios, considering downside risk and risk-free rates (based on `bond-rate.csv`).

For detailed formulas and explanations, please refer to the [`docs/scoring.md`](docs/scoring.md) file.

## 📂 Project Structure

```
mts-challenge/
├── docs/                     # Documentation (e.g., scoring.md)
├── prism-evaluation/         # Python scripts for portfolio evaluation
├── prism-llm/                # Python LLM server (context generation)
├── prism-postgres_init/      # Database initialization scripts
├── prism-postgres_scripts/   # Utility scripts for database management
├── prism-server/             # Go backend API server
├── prism-website/            # Next.js frontend leaderboard
├── docker-compose.yml        # Docker Compose configuration
├── starter.py                # Example script for participants
├── benchmark.py              # API latency benchmarking script
└── README.md                 # This file
```

## 🤔 FAQ

- **Q: How do I get an API key?**
  - A: API keys are typically distributed to teams by the challenge administrators. Administrators can use the `prism-postgres_scripts/add_user.sh` script to create new teams and keys.
- **Q: What are the main API endpoints?**
  - A: GET `/request` (port 8082) for context, POST `/submit` (port 8082) for portfolios, GET `/info` (port 8082) for team status. Remember the `X-API-Code` header!
- **Q: How is my portfolio scored?**
  - A: Scoring considers RoI, Diversification, Client Satisfaction (Risk), and Risk-Adjusted Returns (Sharpe/Sortino). See [`docs/scoring.md`](docs/scoring.md) for details.
- **Q: What data do I get to help design the portfolio?**
  - A: The GET `/request` endpoint provides a client context, including budget, investment timeframe, age, salary, employment status, and industry dislikes. You will need to source market data (e.g., via Polygon.io) for stock performance analysis.
- **Q: How do I run the entire project locally?**
  - A: The recommended method is using Docker Compose. Follow the steps in the [Setup & Running](#️-setup--running) section.

# Docker instructions

`docker compose up --build -d`
`docker compose exec prism-server bash`

# Docker instructions

`docker compose up --build -d`
`docker compose exec prism-server bash`
