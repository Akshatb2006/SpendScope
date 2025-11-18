# Personal Finance Aggregator - Complete System Flow Explanation

## 🎯 Overview: How Everything Connects

Think of this system like a **mini-Plaid** - it simulates connecting to banks, pulling transactions, and organizing your finances.

---

## 📊 High-Level Architecture

```
┌─────────────┐
│   User UI   │ (Frontend - not built yet)
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────────────────────┐
│          FastAPI Backend (main.py)              │
│  - Authentication                               │
│  - API Endpoints (/accounts, /transactions)     │
└──────┬──────────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────────┐
│           Core Services Layer                   │
│  - sync_service.py                              │
│  - categorization_service.py                    │
│  - budget_service.py                            │
│  - anomaly_service.py                           │
└──────┬──────────────────────────────────────────┘
       │
       ├──────────────┬──────────────┬─────────────┐
       ↓              ↓              ↓             ↓
┌─────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ PostgreSQL  │ │  Redis   │ │Mock Banks│ │Scheduler │
│  Database   │ │  Cache   │ │Providers │ │APScheduler│
└─────────────┘ └──────────┘ └──────────┘ └──────────┘
```

---

## 🔄 Complete Flow: Step-by-Step

### **Phase 1: User Registration & Login**

```
1. User → POST /auth/register
   {
     "email": "user@example.com",
     "password": "secure123",
     "full_name": "John Doe"
   }

2. Backend:
   - Hashes password (bcrypt)
   - Stores in PostgreSQL users table
   - Returns user data

3. User → POST /auth/login
   - Verifies password
   - Returns JWT token (valid 30 mins)
   
4. User stores token → Uses in all future requests
```

---

### **Phase 2: Linking a Bank Account (OAuth Simulation)**

```
Step 1: User Clicks "Link Bank"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Frontend → GET /oauth/authorize?provider_id=banka&user_id=1

Backend (oauth_simulator.py):
- Generates auth_code = "abc123xyz..."
- Stores: {
    "abc123xyz": {
      "provider_id": "banka",
      "user_id": 1,
      "expires_at": 5 minutes from now
    }
  }
- Returns: {
    "auth_url": "/oauth/callback?code=abc123xyz",
    "state": "random_state"
  }

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 2: User "Approves" Connection
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Frontend → POST /oauth/callback
{
  "code": "abc123xyz",
  "state": "random_state"
}

Backend (oauth_simulator.py):
1. Validates auth_code
2. Generates access_token = "long_secure_token_xyz..."
3. Stores access_token mapping
4. Calls provider.fetch_accounts(access_token)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 3: Fetch Accounts from Mock Bank
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Provider (banka_provider.py):
def fetch_accounts(token):
    # Returns FAKE data (no real API call)
    return [
        {
            "acct_id": "BA_CHK_001",
            "acct_type": "checking",
            "acct_name": "Premier Checking",
            "current_balance": 5420.50,
            "curr": "USD"
        },
        {
            "acct_id": "BA_SAV_002",
            "acct_type": "savings",
            "acct_name": "Savings Account",
            "current_balance": 12000.00,
            "curr": "USD"
        }
    ]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 4: Save to Database
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Backend:
- Encrypts access_token
- Creates Account records in PostgreSQL:

accounts table:
| id | user_id | provider_id | provider_account_id | name              | balance  |
|----|---------|-------------|---------------------|-------------------|----------|
| 1  | 1       | banka       | BA_CHK_001          | Premier Checking  | 5420.50  |
| 2  | 1       | banka       | BA_SAV_002          | Savings Account   | 12000.00 |
```

---

### **Phase 3: Syncing Transactions (The Magic Happens Here!)**

#### **Automatic Sync (Every 15 minutes)**

```
APScheduler Job (sync_job.py) runs:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Get all active accounts from database
2. For each account:
   - Call SyncService.sync_account(account_id)
```

#### **Inside sync_account() - The Pipeline**

```python
SyncService.sync_account(account_id=1):

Step 1: Get Account from DB
━━━━━━━━━━━━━━━━━━━━━━━━
account = {
    id: 1,
    provider_id: "banka",
    provider_account_id: "BA_CHK_001",
    access_token_encrypted: "encrypted_token...",
    last_synced: "2024-11-15 10:00:00"
}

Step 2: Get Provider & Normalizer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
provider = BankAProvider()  # Mock bank interface
normalizer = BankANormalizer()  # Schema converter

Step 3: Decrypt Token
━━━━━━━━━━━━━━━━━━━━━━━━
access_token = decrypt_token(account.access_token_encrypted)
# Returns: "long_secure_token_xyz..."

Step 4: Fetch Transactions from Mock Bank
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
raw_transactions = provider.fetch_transactions(
    token=access_token,
    account_id="BA_CHK_001",
    since_date="2024-11-15 10:00:00"
)

# BankAProvider returns FAKE data:
[
    {
        "txn_id": "BA_TXN_12345",
        "txn_date": "2024-11-18T09:30:00",
        "txn_amount": -75.50,
        "txn_desc": "Whole Foods Market",
        "merchant_info": "Whole Foods",
        "txn_status": "completed"
    },
    {
        "txn_id": "BA_TXN_12346",
        "txn_date": "2024-11-18T14:20:00",
        "txn_amount": -45.00,
        "txn_desc": "Shell Gas Station",
        "merchant_info": "Shell",
        "txn_status": "completed"
    },
    # ... more transactions
]

Step 5: Normalize Each Transaction
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
for raw_txn in raw_transactions:
    # Convert Bank A's weird format → Standard format
    normalized = normalizer.normalize_transaction(raw_txn)
    
    # Output:
    {
        "date": datetime(2024, 11, 18, 9, 30),
        "amount": -75.50,
        "description": "Whole Foods Market",
        "merchant": "Whole Foods",
        "category": None  # Will be added next
    }

Step 6: Generate Hash for Deduplication
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
txn_hash = SHA256(
    date + amount + description + provider_id
)
# Output: "a1b2c3d4e5f6..."

Step 7: Check if Duplicate
━━━━━━━━━━━━━━━━━━━━━━━━━
if hash exists in database:
    skip this transaction  # Already processed
    records_deduplicated++
else:
    continue processing

Step 8: Categorize Transaction
━━━━━━━━━━━━━━━━━━━━━━━━━━
category = CategorizationService.categorize(
    description="Whole Foods Market",
    merchant="Whole Foods",
    amount=-75.50
)

# Logic inside categorize():
if "whole foods" in description.lower():
    return "groceries"
elif "starbucks" in description.lower():
    return "dining"
# ... more rules

# Output: "groceries"

Step 9: Save to Database
━━━━━━━━━━━━━━━━━━━━━━━
transaction = Transaction(
    account_id=1,
    provider_txn_id="BA_TXN_12345",
    date=datetime(2024, 11, 18, 9, 30),
    amount=-75.50,
    description="Whole Foods Market",
    merchant="Whole Foods",
    category="groceries",
    hash="a1b2c3d4e5f6...",
    status="posted"
)
db.add(transaction)
db.commit()

Step 10: Update Budget
━━━━━━━━━━━━━━━━━━━━━
BudgetService.update_budget_spending(
    user_id=1,
    category="groceries",
    amount=-75.50
)

# Inside update_budget_spending():
budget = get_budget(user_id=1, category="groceries")
# {
#   category: "groceries",
#   amount: 500.00,
#   current_spend: 250.00
# }

budget.current_spend += 75.50  # Now 325.50

if budget.current_spend >= budget.amount:
    send_alert("Budget exceeded!")

Step 11: Log Sync Result
━━━━━━━━━━━━━━━━━━━━━━━
SyncCursor(
    account_id=1,
    status="success",
    records_fetched=10,
    records_inserted=8,
    records_deduplicated=2,
    duration_seconds=2.5
)
```

---

### **Phase 4: Viewing Transactions (User Queries Data)**

```
User → GET /transactions?category=groceries&limit=10

Backend Flow:
━━━━━━━━━━━━

1. Verify JWT token → Get user_id

2. Query database:
   SELECT * FROM transactions t
   JOIN accounts a ON t.account_id = a.id
   WHERE a.user_id = 1
   AND t.category = 'groceries'
   ORDER BY t.date DESC
   LIMIT 10

3. Check Redis cache first:
   cache_key = "user:1:transactions:groceries:10"
   
   if cache.exists(cache_key):
       return cache.get(cache_key)  # Fast!
   else:
       result = query_database()
       cache.set(cache_key, result, ttl=300)  # 5 min cache
       return result

4. Return JSON:
[
    {
        "id": 123,
        "date": "2024-11-18T09:30:00",
        "amount": -75.50,
        "description": "Whole Foods Market",
        "merchant": "Whole Foods",
        "category": "groceries",
        "account_id": 1
    },
    ...
]
```

---

### **Phase 5: Budget Alerts (Real-time)**

```
When transaction is processed:
━━━━━━━━━━━━━━━━━━━━━━━━━━━

if transaction.category == "groceries":
    budget = get_budget(user_id, "groceries")
    budget.current_spend += abs(transaction.amount)
    
    percentage = (budget.current_spend / budget.amount) * 100
    
    if percentage >= 100 and not budget.alert_sent:
        # Publish to Redis pub/sub
        redis.publish("alerts", {
            "type": "budget_alert",
            "user_id": 1,
            "category": "groceries",
            "percentage": 105.5,
            "message": "You've exceeded your groceries budget!"
        })
        
        budget.alert_sent = True

# Alert Job (runs every minute):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
subscribe to "alerts" channel
if message received:
    send_email(user.email, message)
    send_push_notification(user.device_token, message)
```

---

### **Phase 6: Anomaly Detection**

```
User → GET /anomalies/account/1

Backend:
━━━━━━━━

1. Get last 90 days of transactions for account

2. Group by category:
   groceries: [-50, -45, -52, -48, -51, ...]
   dining: [-25, -30, -28, -27, ...]

3. For each recent transaction:
   - Calculate mean & std deviation of historical data
   - Calculate z-score: (amount - mean) / std_dev
   
   Example:
   groceries mean = $50
   groceries std_dev = $5
   new transaction = $250
   
   z-score = (250 - 50) / 5 = 40 (!!!)
   
   if z-score > 2:
       flag as anomaly

4. Check for new merchants:
   historical_merchants = ["Whole Foods", "Safeway", "Trader Joe's"]
   new_transaction.merchant = "Random Store XYZ"
   
   if merchant not in historical_merchants:
       flag as "new_merchant" anomaly

5. Return anomalies:
[
    {
        "transaction_id": 456,
        "type": "unusual_amount",
        "description": "$250 is 40 std deviations from normal",
        "severity": "high"
    },
    {
        "transaction_id": 457,
        "type": "new_merchant",
        "description": "First transaction with Random Store XYZ",
        "severity": "medium"
    }
]
```

---

## 🏦 How Fake Banks Work

### **Mock Bank Architecture**

```python
# All mock banks implement the same interface:

class BaseProvider(ABC):
    @abstractmethod
    def fetch_accounts(token: str) -> List[Dict]:
        pass
    
    @abstractmethod
    def fetch_transactions(token, account_id, since_date) -> List[Dict]:
        pass

# Bank A returns data in ITS format:
class BankAProvider(BaseProvider):
    def fetch_accounts(self, token):
        return [{
            "acct_id": "BA_001",          # Bank A's field name
            "acct_type": "checking",      # Bank A's field name
            "current_balance": 5420.50,   # Bank A's field name
            "curr": "USD"                 # Bank A's field name
        }]

# Bank B returns data in DIFFERENT format:
class BankBProvider(BaseProvider):
    def fetch_accounts(self, token):
        return [{
            "account_number": "BB_001",   # Different name!
            "type": "credit",             # Different name!
            "balance_amount": -1250.75,   # Different name!
            "currency_code": "USD"        # Different name!
        }]

# Each bank has a NORMALIZER that converts to standard format:
class BankANormalizer:
    def normalize_account(self, raw):
        return AccountCreate(
            provider_account_id=raw["acct_id"],        # ← converts
            account_type=raw["acct_type"],              # ← converts
            balance=raw["current_balance"],             # ← converts
            currency=raw["curr"]                        # ← converts
        )

# This is the ADAPTER PATTERN!
```

---

## 🗄️ Database Schema Relationships

```sql
users
├── id (PK)
├── email
├── hashed_password
└── full_name

accounts
├── id (PK)
├── user_id (FK → users.id)          ← Links to user
├── provider_id ("banka", "bankb")
├── provider_account_id
├── balance
└── access_token_encrypted

transactions
├── id (PK)
├── account_id (FK → accounts.id)    ← Links to account
├── provider_txn_id
├── date
├── amount
├── description
├── category
└── hash (for deduplication)

budgets
├── id (PK)
├── user_id (FK → users.id)          ← Links to user
├── category_name
├── amount
├── current_spend
└── period (weekly/monthly)

audit_logs
├── id (PK)
├── transaction_id (FK → transactions.id)
├── field_changed
├── old_value
├── new_value
└── reason

sync_cursors
├── id (PK)
├── account_id (FK → accounts.id)
├── last_sync_date
├── status
└── records_fetched
```

---

## 🔐 Security Flow

```
1. User Login
   ↓
2. Server generates JWT token
   token = {
       "sub": user_id,
       "exp": 30 minutes from now
   }
   signed with SECRET_KEY
   ↓
3. User stores token
   ↓
4. Every API request:
   Headers: { "Authorization": "Bearer <token>" }
   ↓
5. Server verifies token:
   - Checks signature
   - Checks expiration
   - Extracts user_id
   ↓
6. Query uses user_id to filter data:
   WHERE accounts.user_id = <user_id>
```

---

## 🎭 Why Everything is Fake (But Realistic)

```
Real Plaid:
- Connects to actual banks via Screen Scraping or APIs
- Banks: Chase, Wells Fargo, BofA, etc.
- Real transactions from real accounts

Our System:
- Connects to SIMULATED banks (Python classes)
- Banks: BankA, BankB, BankC (made-up names)
- Generates FAKE but realistic transactions

Why?
- No bank API credentials needed
- No legal/compliance issues
- Perfect for learning & testing
- Works offline
- Free to run

But the ARCHITECTURE is identical to real systems!
```

---

## 📊 Data Generation

```python
# How fake transactions are created:

TransactionGenerator.generate_transactions(
    account_id="ACC_001",
    start_date=datetime(2024, 1, 1),
    days=30,
    daily_count=3
)

# Generates realistic patterns:
- Groceries: -$50 to -$150 (random within range)
- Dining: -$15 to -$50
- Gas: -$30 to -$80
- Income: +$2000 to +$5000 (on day 1 and 15)

# Merchants are randomly chosen from lists:
groceries: ["Whole Foods", "Safeway", "Trader Joe's"]
dining: ["Starbucks", "Chipotle", "Panera"]

# Dates are spread across the month
# Categories are varied
# Amounts are realistic

Result: Looks like real bank data!
```

---

## 🚀 Summary

1. **User signs up** → Stored in PostgreSQL
2. **User links bank** → OAuth simulation creates access token
3. **Mock bank returns fake data** → Matches real bank data format
4. **Normalizer converts** → Bank A format → Standard format
5. **Deduplicator checks hash** → Prevents duplicates
6. **Categorizer assigns category** → Rule-based (groceries, dining, etc.)
7. **Budget tracker updates** → Checks if over budget → Sends alert
8. **Anomaly detector runs** → Statistical analysis → Flags unusual transactions
9. **User queries data** → Fast (Redis cache) or DB → Returns JSON

**Everything is connected through:**
- Database relationships (Foreign Keys)
- Service layer (Python classes)
- API endpoints (FastAPI routes)
- Background jobs (APScheduler)
- Real-time alerts (Redis pub/sub)

It's a **complete, production-ready system** that simulates Plaid! 🎉
