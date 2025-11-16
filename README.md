# Personal Finance Aggregator (Plaid-Style Mock Platform)

A fully-simulated financial data aggregation backend with OAuth-style linking, mock banks, scheduled sync jobs, schema normalization, categorization, budgeting, anomaly detection, and synthetic transaction generation.

## 📌 Overview

This project is a complete Plaid-like personal finance aggregation platform, built entirely with **FastAPI**, **PostgreSQL**, **Redis**, and **APScheduler**. It simulates connecting multiple banks, pulling financial data, normalizing schemas, deduplicating transactions, tracking deltas, categorizing spending, enforcing budgets, and detecting anomalies. 

All banks are mock providers, and all transaction streams are synthetically generated, making the entire platform self-contained and perfect for learning system design, data pipelines, and financial intelligence logic.

## 🎯 Key Features

### 🔗 1. OAuth-Style Bank Linking (Simulated)
- Users "connect" mock banks through an OAuth-like flow
- Token exchange & secure storage
- Provider registry for plugging in new mock banks

### 🏦 2. Mock Bank Providers
Each mock bank exposes its own schema (intentionally inconsistent) to simulate real-world integration challenges.

**Examples:**
- `BankAProvider`
- `BankBProvider`
- `BankCProvider`

**Endpoints:**
- `GET /accounts`
- `GET /transactions`

### 🗃️ 3. Schema Normalization
Convert each provider's schema → unified canonical models:
- Account Model
- Transaction Model

Built using structured Pydantic normalizers per provider.

### 🧹 4. Deduplication + Delta History
- Transaction hashing (SHA-256)
- Prevention of duplicates
- Track corrected transactions (amount, description, status changes)
- Immutable event log for auditability

### 🔁 5. Scheduled Sync Engine
Powered by **APScheduler**:
- Polls providers every 15 minutes
- Pulls latest transactions
- Normalizes
- Dedupes
- Writes deltas
- Updates user balances
- Includes Redis-based locking to avoid duplicate job runs

### 🧠 6. Rules-Based Categorization
- Keyword matching
- Merchant heuristics
- Regex patterns
- Amount-based classification
- **Goal:** ≥ 90% category precision
- User overrides supported with persistent rules

### 💸 7. Budgeting System + Real-Time Alerts
- User budgets per category (weekly/monthly)
- Spend tracking
- Alerts dispatched within 1 minute of budget breach
- Redis event stream for fast notifications

### 🚨 8. Anomaly Detection (Simple Heuristics)
- Sudden unusually high spend
- New merchant anomalies
- Outlier detection (z-score / MAD)
- Human-readable explainers

### 🧾 9. Reconciliation & Audit Trail
- Users can correct transactions
- Original provider data remains untouched
- All corrections stored in audit logs
- Transparent history of every change

### 🧬 10. Synthetic Transaction Generator
Generate realistic transactions for testing:
- Salaries
- Groceries
- Rent
- UPI/PayTM/Stripe-like payments
- Subscriptions
- Random anomalies
- Duplicate seeds
- Corrected transactions

Used to populate mock banks for development & testing.

## 🧱 Tech Stack

- **Backend:** FastAPI, Uvicorn
- **Database:** PostgreSQL + SQLAlchemy ORM
- **Cache & IPC:** Redis
- **Scheduling:** APScheduler
- **Serialization:** Pydantic
- **Testing:** pytest

## 🏗️ System Architecture

```
┌───────────────────────────┐
│      Client / UI          │
└──────────────┬────────────┘
               │
       (FastAPI Gateway)
               │
┌──────────────┼──────────────────┐
│              │                  │
│    Sync Pipeline         Core Services         Reporting APIs
│              │                  │
│   ┌──────────┼─────────┐  ┌────┼─────┐  ┌──────────┼──────────┐
│   │ Providers (Mock)   │  │ Budgeting │  │ Anomalies / Stats   │
│   │ Normalization      │  │ Categoriz │  │ Audit Logs          │
│   │ Dedup / Delta      │  │ Reconcile │  │                     │
│   └──────────┼─────────┘  └────┼─────┘  └──────────┼──────────┘
│              │                  │                   │
└──────────────┴──────────────────┴───────────────────┘
                        │
                 PostgreSQL + Redis
```

## 📁 Folder Structure

```
app/
├── main.py
├── config.py
├── database.py
├── cache.py
│
├── core/
│   ├── security.py
│   ├── oauth_simulator.py
│   └── utils.py
│
├── models/
├── schemas/
├── routers/
│
├── providers/              # Mock banks
│   ├── banka_provider.py
│   ├── bankb_provider.py
│   └── bankc_provider.py
│
├── normalization/
│   ├── banka_normalizer.py
│   ├── bankb_normalizer.py
│   └── bankc_normalizer.py
│
├── services/
│   ├── sync_service.py
│   ├── dedup_service.py
│   ├── categorization_service.py
│   ├── budget_service.py
│   ├── anomaly_service.py
│   └── reconciliation_service.py
│
├── jobs/
│   ├── scheduler.py
│   └── sync_job.py
│
├── generator/
│   ├── transaction_generator.py
│   └── seed_data.py
│
└── tests/
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL
- Redis

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/personal-finance-aggregator.git
cd personal-finance-aggregator
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your database and Redis configurations
```

4. **Run database migrations**
```bash
# Add instructions if using Alembic
alembic upgrade head
```

5. **Start the server**
```bash
uvicorn app.main:app --reload
```

6. **Start the scheduler** (in a separate terminal)
```bash
python -m app.jobs.scheduler
```

7. **Access the API documentation**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📊 Performance KPIs

- **Categorization accuracy:** ≥ 90%
- **Budget breach alert latency:** ≤ 1 minute
- **Deduplication accuracy:** ≥ 99.5%
- **Median API latency:** ≤ 150 ms
- **Sync run duration:** < 3 seconds per provider

## 🧪 Testing

Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app tests/
```

## 📝 API Endpoints

### Authentication
- `POST /auth/link-bank` - Initiate OAuth flow with mock bank
- `POST /auth/callback` - Handle OAuth callback

### Accounts
- `GET /accounts` - List all linked accounts
- `GET /accounts/{account_id}` - Get account details

### Transactions
- `GET /transactions` - List transactions with filters
- `GET /transactions/{transaction_id}` - Get transaction details
- `POST /transactions/{transaction_id}/reconcile` - Correct transaction

### Budgets
- `GET /budgets` - List budgets
- `POST /budgets` - Create budget
- `PUT /budgets/{budget_id}` - Update budget
- `DELETE /budgets/{budget_id}` - Delete budget

### Analytics
- `GET /analytics/spending` - Spending analysis
- `GET /analytics/anomalies` - Detected anomalies
- `GET /analytics/categories` - Category breakdown

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by Plaid's financial data aggregation platform
- Built for educational purposes and system design learning
