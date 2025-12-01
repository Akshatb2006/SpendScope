# Database Migration Guide

## 🔧 Fixing the is_active Column Type Issue

The `is_active` column in the `accounts` table was defined as `INTEGER` (from SQLite days) but needs to be `BOOLEAN` for PostgreSQL.

---

## ✅ What Was Fixed:

1. **Updated Model:** Changed `app/models/account.py` to use `Boolean` type
2. **Created Migration Scripts:** Added SQL and Python scripts to update the database

---

## 🚀 Option 1: Run Migration from Render Shell (Recommended)

### Steps:

1. **Go to your Render dashboard**
2. **Click on your SpendScope web service**
3. **Click "Shell" in the top menu**
4. **Run these commands:**

```bash
# Download the migration script
cd /opt/render/project/src

# Run the Python migration
python migrations/run_migration.py
```

The script will:
- ✅ Connect to your PostgreSQL database
- ✅ Convert `is_active` from INTEGER to BOOLEAN
- ✅ Verify the changes
- ✅ Show before/after schema

---

## 🚀 Option 2: Run Migration Locally

### Steps:

1. **Set your database URL:**
```bash
export DATABASE_URL="postgresql://spendscope_db_user:pshR3Ep2PpldgUi7NY8tDPYgWfWR6Lgw@dpg-d4mhv13e5dus738bm38g-a.oregon-postgres.render.com/spendscope_db"
```

2. **Run the migration:**
```bash
python migrations/run_migration.py
```

---

## 🚀 Option 3: Manual SQL Migration

If you prefer running SQL directly:

1. **Connect to your PostgreSQL database:**
```bash
psql postgresql://spendscope_db_user:pshR3Ep2PpldgUi7NY8tDPYgWfWR6Lgw@dpg-d4mhv13e5dus738bm38g-a.oregon-postgres.render.com/spendscope_db
```

2. **Run this SQL:**
```sql
ALTER TABLE accounts 
ALTER COLUMN is_active TYPE BOOLEAN 
USING CASE 
    WHEN is_active = 0 THEN FALSE 
    ELSE TRUE 
END;

ALTER TABLE accounts 
ALTER COLUMN is_active SET DEFAULT TRUE;
```

3. **Verify:**
```sql
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'accounts' AND column_name = 'is_active';
```

---

## 📊 After Migration:

Once the migration completes:

1. **Render will auto-deploy** with the new code (already pushed)
2. **The sync job will work correctly**
3. **No more "operator does not exist: integer = boolean" errors**

---

## ✅ Verification:

After running the migration, check your Render logs. You should see:
- ✅ Sync jobs running without errors
- ✅ `is_active = true` queries working
- ✅ No type mismatch errors

---

## 🎯 Quick Test:

Test the fix by calling:
```bash
curl https://spendscope-zp32.onrender.com/accounts
```

The response should work without database errors!

---

**Need help?** Let me know which option you'd like to use and I can guide you through it step-by-step.
