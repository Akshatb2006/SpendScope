#!/bin/bash
# SpendScope API Testing Script
# Complete test suite for all API endpoints
# 
# Usage: bash test_api.sh [BASE_URL]
# Example: bash test_api.sh https://spendscope-zp32.onrender.com
#          bash test_api.sh http://localhost:8000

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base URL (use argument or default to production)
BASE_URL="${1:-https://spendscope-zp32.onrender.com}"

# Variables to store tokens and IDs
USER_TOKEN=""
USER_ID=""
ACCOUNT_ID=""
TRANSACTION_ID=""
BUDGET_ID=""
CATEGORY_ID=""

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}SpendScope API Testing Script${NC}"
echo -e "${BLUE}================================${NC}"
echo -e "Base URL: ${YELLOW}$BASE_URL${NC}\n"

# Helper function to print test results
print_result() {
    local test_name=$1
    local status_code=$2
    local expected=$3
    
    if [ "$status_code" -eq "$expected" ] || [ "$status_code" -eq 200 ] || [ "$status_code" -eq 201 ]; then
        echo -e "${GREEN}✓${NC} $test_name (Status: $status_code)"
    else
        echo -e "${RED}✗${NC} $test_name (Status: $status_code, Expected: $expected)"
    fi
}

# Helper function to make requests and parse response
make_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    local headers=$4
    
    if [ -n "$headers" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -H "$headers" \
            -d "$data" 2>/dev/null)
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null)
    fi
    
    echo "$response"
}

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}1. Basic Health Checks${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Test 1: Root endpoint
echo -e "${YELLOW}Testing root endpoint...${NC}"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/" 2>/dev/null)
status_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | sed '$d')
print_result "GET /" "$status_code" 200
echo "$body" | jq '.' 2>/dev/null || echo "$body"
echo ""

# Test 2: Health check
echo -e "${YELLOW}Testing health check...${NC}"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/health" 2>/dev/null)
status_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | sed '$d')
print_result "GET /health" "$status_code" 200
echo "$body" | jq '.' 2>/dev/null || echo "$body"
echo ""

# Test 3: List providers
echo -e "${YELLOW}Testing providers endpoint...${NC}"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/providers" 2>/dev/null)
status_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | sed '$d')
print_result "GET /providers" "$status_code" 200
echo "$body" | jq '.' 2>/dev/null || echo "$body"
echo ""

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}2. Authentication${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Generate random email to avoid conflicts
RANDOM_EMAIL="test_$(date +%s)@example.com"

# Test 4: Register user
echo -e "${YELLOW}Testing user registration...${NC}"
response=$(make_request POST "/auth/register" "{
  \"email\": \"$RANDOM_EMAIL\",
  \"password\": \"SecurePass123!\",
  \"full_name\": \"Test User\"
}")
status_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | sed '$d')
print_result "POST /auth/register" "$status_code" 200
echo "$body" | jq '.' 2>/dev/null || echo "$body"
echo ""

# Test 5: Login
echo -e "${YELLOW}Testing user login...${NC}"
response=$(make_request POST "/auth/login" "{
  \"email\": \"$RANDOM_EMAIL\",
  \"password\": \"SecurePass123!\"
}")
status_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | sed '$d')
print_result "POST /auth/login" "$status_code" 200
echo "$body" | jq '.' 2>/dev/null || echo "$body"

# Extract token
USER_TOKEN=$(echo "$body" | jq -r '.access_token' 2>/dev/null)
if [ -n "$USER_TOKEN" ] && [ "$USER_TOKEN" != "null" ]; then
    echo -e "${GREEN}Token acquired: ${USER_TOKEN:0:20}...${NC}"
else
    echo -e "${RED}Failed to get authentication token${NC}"
fi
echo ""

# If we don't have a token, try logging in with test user
if [ -z "$USER_TOKEN" ] || [ "$USER_TOKEN" == "null" ]; then
    echo -e "${YELLOW}Trying default test credentials...${NC}"
    response=$(make_request POST "/auth/login" "{
      \"email\": \"test@example.com\",
      \"password\": \"testpassword\"
    }")
    status_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | sed '$d')
    USER_TOKEN=$(echo "$body" | jq -r '.access_token' 2>/dev/null)
    
    if [ -n "$USER_TOKEN" ] && [ "$USER_TOKEN" != "null" ]; then
        echo -e "${GREEN}Token acquired with default credentials${NC}"
    fi
    echo ""
fi

# Set authorization header
AUTH_HEADER="Authorization: Bearer $USER_TOKEN"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}3. Accounts Management${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Test 6: Link bank account (simulated)
echo -e "${YELLOW}Testing bank linking...${NC}"
response=$(make_request POST "/auth/link-bank" "{
  \"provider_id\": \"banka\",
  \"user_credentials\": {
    \"username\": \"testuser\",
    \"password\": \"testpass\"
  }
}" "$AUTH_HEADER")
status_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | sed '$d')
print_result "POST /auth/link-bank" "$status_code" 200
echo "$body" | jq '.' 2>/dev/null || echo "$body"
echo ""

# Test 7: List accounts
echo -e "${YELLOW}Testing list accounts...${NC}"
response=$(curl -s -w "\n%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/accounts" 2>/dev/null)
status_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | sed '$d')
print_result "GET /accounts" "$status_code" 200
echo "$body" | jq '.' 2>/dev/null || echo "$body"

# Extract first account ID
ACCOUNT_ID=$(echo "$body" | jq -r '.[0].id' 2>/dev/null)
if [ -n "$ACCOUNT_ID" ] && [ "$ACCOUNT_ID" != "null" ]; then
    echo -e "${GREEN}Account ID: $ACCOUNT_ID${NC}"
fi
echo ""

# Test 8: Get specific account
if [ -n "$ACCOUNT_ID" ] && [ "$ACCOUNT_ID" != "null" ]; then
    echo -e "${YELLOW}Testing get account details...${NC}"
    response=$(curl -s -w "\n%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/accounts/$ACCOUNT_ID" 2>/dev/null)
    status_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | sed '$d')
    print_result "GET /accounts/{id}" "$status_code" 200
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
    echo ""
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}4. Transactions${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Test 9: List transactions
echo -e "${YELLOW}Testing list transactions...${NC}"
response=$(curl -s -w "\n%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/transactions" 2>/dev/null)
status_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | sed '$d')
print_result "GET /transactions" "$status_code" 200
echo "$body" | jq '.[0:3]' 2>/dev/null || echo "$body" | head -20

# Extract first transaction ID
TRANSACTION_ID=$(echo "$body" | jq -r '.[0].id' 2>/dev/null)
if [ -n "$TRANSACTION_ID" ] && [ "$TRANSACTION_ID" != "null" ]; then
    echo -e "${GREEN}Transaction ID: $TRANSACTION_ID${NC}"
fi
echo ""

# Test 10: Get specific transaction
if [ -n "$TRANSACTION_ID" ] && [ "$TRANSACTION_ID" != "null" ]; then
    echo -e "${YELLOW}Testing get transaction details...${NC}"
    response=$(curl -s -w "\n%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/transactions/$TRANSACTION_ID" 2>/dev/null)
    status_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | sed '$d')
    print_result "GET /transactions/{id}" "$status_code" 200
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
    echo ""
fi

# Test 11: Filter transactions by category
echo -e "${YELLOW}Testing filter transactions by category...${NC}"
response=$(curl -s -w "\n%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/transactions?category=groceries" 2>/dev/null)
status_code=$(echo "$response" | tail -n 1)
print_result "GET /transactions?category=groceries" "$status_code" 200
echo ""

# Test 12: Filter transactions by date range
echo -e "${YELLOW}Testing filter transactions by date...${NC}"
START_DATE="2024-01-01"
END_DATE="2024-12-31"
response=$(curl -s -w "\n%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/transactions?start_date=$START_DATE&end_date=$END_DATE" 2>/dev/null)
status_code=$(echo "$response" | tail -n 1)
print_result "GET /transactions?start_date&end_date" "$status_code" 200
echo ""

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}5. Categories${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Test 13: List categories
echo -e "${YELLOW}Testing list categories...${NC}"
response=$(curl -s -w "\n%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/categories" 2>/dev/null)
status_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | sed '$d')
print_result "GET /categories" "$status_code" 200
echo "$body" | jq '.' 2>/dev/null || echo "$body"

# Extract category ID
CATEGORY_ID=$(echo "$body" | jq -r '.[0].id' 2>/dev/null)
echo ""

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}6. Budgets${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Test 14: Create budget
echo -e "${YELLOW}Testing create budget...${NC}"
response=$(make_request POST "/budgets/" "{
  \"category_name\": \"groceries\",
  \"amount\": 500.00,
  \"period\": \"monthly\"
}" "$AUTH_HEADER")
status_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | sed '$d')
print_result "POST /budgets/" "$status_code" 200
echo "$body" | jq '.' 2>/dev/null || echo "$body"

# Extract budget ID
BUDGET_ID=$(echo "$body" | jq -r '.id' 2>/dev/null)
if [ -n "$BUDGET_ID" ] && [ "$BUDGET_ID" != "null" ]; then
    echo -e "${GREEN}Budget ID: $BUDGET_ID${NC}"
fi
echo ""

# Test 15: List budgets
echo -e "${YELLOW}Testing list budgets...${NC}"
response=$(curl -s -w "\n%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/budgets" 2>/dev/null)
status_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | sed '$d')
print_result "GET /budgets" "$status_code" 200
echo "$body" | jq '.' 2>/dev/null || echo "$body"
echo ""

# Test 16: Get budget status
if [ -n "$BUDGET_ID" ] && [ "$BUDGET_ID" != "null" ]; then
    echo -e "${YELLOW}Testing get budget status...${NC}"
    response=$(curl -s -w "\n%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/budgets/$BUDGET_ID/status" 2>/dev/null)
    status_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | sed '$d')
    print_result "GET /budgets/{id}/status" "$status_code" 200
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
    echo ""
fi

# Test 17: Update budget
if [ -n "$BUDGET_ID" ] && [ "$BUDGET_ID" != "null" ]; then
    echo -e "${YELLOW}Testing update budget...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X PUT -H "Content-Type: application/json" \
        -H "$AUTH_HEADER" "$BASE_URL/budgets/$BUDGET_ID" \
        -d "{\"amount\": 600.00}" 2>/dev/null)
    status_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | sed '$d')
    print_result "PUT /budgets/{id}" "$status_code" 200
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
    echo ""
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}7. Analytics & Anomalies${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Test 18: Get spending analysis
echo -e "${YELLOW}Testing spending analysis...${NC}"
response=$(curl -s -w "\n%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/analytics/spending" 2>/dev/null)
status_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | sed '$d')
print_result "GET /analytics/spending" "$status_code" 200
echo "$body" | jq '.' 2>/dev/null || echo "$body"
echo ""

# Test 19: Get category breakdown
echo -e "${YELLOW}Testing category breakdown...${NC}"
response=$(curl -s -w "\n%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/analytics/categories" 2>/dev/null)
status_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | sed '$d')
print_result "GET /analytics/categories" "$status_code" 200
echo "$body" | jq '.' 2>/dev/null || echo "$body"
echo ""

# Test 20: Get anomalies
echo -e "${YELLOW}Testing detected anomalies...${NC}"
response=$(curl -s -w "\n%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/analytics/anomalies" 2>/dev/null)
status_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | sed '$d')
print_result "GET /analytics/anomalies" "$status_code" 200
echo "$body" | jq '.' 2>/dev/null || echo "$body"
echo ""

# Test 21: Get account-specific anomalies
if [ -n "$ACCOUNT_ID" ] && [ "$ACCOUNT_ID" != "null" ]; then
    echo -e "${YELLOW}Testing account anomalies...${NC}"
    response=$(curl -s -w "\n%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/anomalies/account/$ACCOUNT_ID" 2>/dev/null)
    status_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | sed '$d')
    print_result "GET /anomalies/account/{id}" "$status_code" 200
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
    echo ""
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}8. Sync Operations${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Test 22: Trigger manual sync
if [ -n "$ACCOUNT_ID" ] && [ "$ACCOUNT_ID" != "null" ]; then
    echo -e "${YELLOW}Testing manual sync trigger...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X POST -H "$AUTH_HEADER" "$BASE_URL/sync/account/$ACCOUNT_ID" 2>/dev/null)
    status_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | sed '$d')
    print_result "POST /sync/account/{id}" "$status_code" 200
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
    echo ""
fi

# Test 23: Get sync status
echo -e "${YELLOW}Testing sync status...${NC}"
response=$(curl -s -w "\n%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/sync/status" 2>/dev/null)
status_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | sed '$d')
print_result "GET /sync/status" "$status_code" 200
echo "$body" | jq '.' 2>/dev/null || echo "$body"
echo ""

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}9. Cleanup (Optional)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Test 24: Delete budget (cleanup)
if [ -n "$BUDGET_ID" ] && [ "$BUDGET_ID" != "null" ]; then
    echo -e "${YELLOW}Testing delete budget...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X DELETE -H "$AUTH_HEADER" "$BASE_URL/budgets/$BUDGET_ID" 2>/dev/null)
    status_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | sed '$d')
    print_result "DELETE /budgets/{id}" "$status_code" 200
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
    echo ""
fi

# Test 25: Unlink account (cleanup)
if [ -n "$ACCOUNT_ID" ] && [ "$ACCOUNT_ID" != "null" ]; then
    echo -e "${YELLOW}Testing unlink account...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X DELETE -H "$AUTH_HEADER" "$BASE_URL/accounts/$ACCOUNT_ID" 2>/dev/null)
    status_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | sed '$d')
    print_result "DELETE /accounts/{id}" "$status_code" 200
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
    echo ""
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Testing Complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "Summary:"
echo -e "  • Base URL: $BASE_URL"
echo -e "  • Token: ${USER_TOKEN:0:20}..."
echo -e "  • View full API docs: $BASE_URL/docs"
echo ""
