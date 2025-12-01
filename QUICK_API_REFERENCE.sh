# Quick API Testing Commands
# SpendScope - Working Endpoints Reference

BASE_URL="https://spendscope-zp32.onrender.com"
# OR for local: BASE_URL="http://localhost:8000"

# ============================================
# STEP 1: Set the TOKEN variable properly
# ============================================
# First, login and copy the FULL token from the response:

curl -X POST $BASE_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'

# Copy the FULL access_token value and set it:
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzY0NTcyODI3fQ.1GZXk5pQP2sVchZvE7RWeQmIUQwh07ybclmfFBR50DY"

# Verify it's set:
echo $TOKEN

# ============================================
# WORKING ENDPOINTS
# ============================================

# --- Authentication (No token needed) ---
# Register
curl -X POST $BASE_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123!",
    "full_name": "New User"
  }'

# Login  
curl -X POST $BASE_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'

# --- Accounts ---
# List accounts
curl -H "Authorization: Bearer $TOKEN" $BASE_URL/accounts

# Get specific account
curl -H "Authorization: Bearer $TOKEN" $BASE_URL/accounts/1

# Link account (note: /accounts/link NOT /auth/link-bank)
curl -X POST $BASE_URL/accounts/link \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider_id": "banka",
    "account_id": "test_account"
  }'

# --- Transactions ---
# List transactions
curl -H "Authorization: Bearer $TOKEN" $BASE_URL/transactions

# Get specific transaction
curl -H "Authorization: Bearer $TOKEN" $BASE_URL/transactions/1

# Get transaction history
curl -H "Authorization: Bearer $TOKEN" $BASE_URL/transactions/1/history

# Reconcile transaction
curl -X POST $BASE_URL/transactions/1/reconcile \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": -55.00,
    "description": "Updated description"
  }'

# Filter by category
curl -H "Authorization: Bearer $TOKEN" \
  "$BASE_URL/transactions?category=groceries"

# Filter by account
curl -H "Authorization: Bearer $TOKEN" \
  "$BASE_URL/transactions?account_id=1"

# --- Categories ---
# List categories
curl -H "Authorization: Bearer $TOKEN" $BASE_URL/categories

# --- Budgets ---
# Create budget
curl -X POST $BASE_URL/budgets/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "category_name": "groceries",
    "amount": 500.00,
    "period": "monthly"
  }'

# List budgets
curl -H "Authorization: Bearer $TOKEN" $BASE_URL/budgets

# Delete budget
curl -X DELETE $BASE_URL/budgets/1 \
  -H "Authorization: Bearer $TOKEN"

# --- Anomalies ---
# Get anomalies for specific account
curl -H "Authorization: Bearer $TOKEN" \
  $BASE_URL/anomalies/account/1

# --- Sync ---
# Manually sync account
curl -X POST $BASE_URL/sync/account/1 \
  -H "Authorization: Bearer $TOKEN"

# Get sync logs for account
curl -H "Authorization: Bearer $TOKEN" \
  $BASE_URL/sync/logs/account/1

# --- Health Checks (No token needed) ---
# Root
curl $BASE_URL/

# Health
curl $BASE_URL/health

# Providers
curl $BASE_URL/providers

# ============================================
# NOTES:
# ============================================
# 1. ALWAYS set TOKEN with: export TOKEN="your_full_token_here"
# 2. There is NO /analytics/* endpoints - use specific routes above
# 3. Account linking is /accounts/link NOT /auth/link-bank
# 4. Add | jq at the end for pretty JSON (if you have jq installed)
