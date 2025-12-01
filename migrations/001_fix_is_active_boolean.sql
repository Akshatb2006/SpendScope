-- Migration: Fix is_active column type from INTEGER to BOOLEAN
-- Date: 2025-12-01
-- Description: Converts the is_active column in accounts table from INTEGER to BOOLEAN

-- Step 1: Alter the column type
-- PostgreSQL will automatically convert 0 -> false and 1/other -> true
ALTER TABLE accounts 
ALTER COLUMN is_active TYPE BOOLEAN 
USING CASE 
    WHEN is_active = 0 THEN FALSE 
    ELSE TRUE 
END;

-- Step 2: Set default value
ALTER TABLE accounts 
ALTER COLUMN is_active SET DEFAULT TRUE;

-- Verify the change
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'accounts' AND column_name = 'is_active';
