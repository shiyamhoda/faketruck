-- ============================================================
-- AutoParts Data Platform
-- Script  : test_sprint1_databases.sql
-- Purpose : Validate Sprint 1 database and schema creation
-- Run in  : SSMS — results show PASS / FAIL per check
-- ============================================================

USE master;
GO

PRINT '========================================';
PRINT ' AutoParts Sprint 1 — Database Tests';
PRINT ' Run at: ' + CONVERT(NVARCHAR, SYSDATETIME(), 120);
PRINT '========================================';
GO

-- -------------------------------------------------------
-- Helper: inline PASS/FAIL output
-- -------------------------------------------------------
DECLARE @passed INT = 0, @failed INT = 0;

-- TEST 1: AutoParts_Staging exists
IF EXISTS (SELECT 1 FROM sys.databases WHERE name = 'AutoParts_Staging')
BEGIN PRINT '[PASS] T01 — AutoParts_Staging database exists'; SET @passed += 1; END
ELSE
BEGIN PRINT '[FAIL] T01 — AutoParts_Staging database NOT found'; SET @failed += 1; END

-- TEST 2: AutoParts_ODS exists
IF EXISTS (SELECT 1 FROM sys.databases WHERE name = 'AutoParts_ODS')
BEGIN PRINT '[PASS] T02 — AutoParts_ODS database exists'; SET @passed += 1; END
ELSE
BEGIN PRINT '[FAIL] T02 — AutoParts_ODS database NOT found'; SET @failed += 1; END

-- TEST 3: AutoParts_DW exists
IF EXISTS (SELECT 1 FROM sys.databases WHERE name = 'AutoParts_DW')
BEGIN PRINT '[PASS] T03 — AutoParts_DW database exists'; SET @passed += 1; END
ELSE
BEGIN PRINT '[FAIL] T03 — AutoParts_DW database NOT found'; SET @failed += 1; END

PRINT '----------------------------------------';
PRINT CONCAT('Results (master): ', @passed, ' passed, ', @failed, ' failed');
PRINT '----------------------------------------';
GO

-- -------------------------------------------------------
-- Staging schema tests
-- -------------------------------------------------------
USE AutoParts_Staging;
GO

DECLARE @passed INT = 0, @failed INT = 0;

IF EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'pos')
BEGIN PRINT '[PASS] T04 — Staging schema [pos] exists'; SET @passed += 1; END
ELSE
BEGIN PRINT '[FAIL] T04 — Staging schema [pos] NOT found'; SET @failed += 1; END

IF EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'ecom')
BEGIN PRINT '[PASS] T05 — Staging schema [ecom] exists'; SET @passed += 1; END
ELSE
BEGIN PRINT '[FAIL] T05 — Staging schema [ecom] NOT found'; SET @failed += 1; END

IF EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'inventory')
BEGIN PRINT '[PASS] T06 — Staging schema [inventory] exists'; SET @passed += 1; END
ELSE
BEGIN PRINT '[FAIL] T06 — Staging schema [inventory] NOT found'; SET @failed += 1; END

IF EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'supplier')
BEGIN PRINT '[PASS] T07 — Staging schema [supplier] exists'; SET @passed += 1; END
ELSE
BEGIN PRINT '[FAIL] T07 — Staging schema [supplier] NOT found'; SET @failed += 1; END

PRINT '----------------------------------------';
PRINT CONCAT('Results (Staging): ', @passed, ' passed, ', @failed, ' failed');
PRINT '----------------------------------------';
GO

-- -------------------------------------------------------
-- ODS schema tests
-- -------------------------------------------------------
USE AutoParts_ODS;
GO

DECLARE @passed INT = 0, @failed INT = 0;

IF EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'ods')
BEGIN PRINT '[PASS] T08 — ODS schema [ods] exists'; SET @passed += 1; END
ELSE
BEGIN PRINT '[FAIL] T08 — ODS schema [ods] NOT found'; SET @failed += 1; END

PRINT '----------------------------------------';
PRINT CONCAT('Results (ODS): ', @passed, ' passed, ', @failed, ' failed');
PRINT '----------------------------------------';
GO

-- -------------------------------------------------------
-- DW schema + table tests
-- -------------------------------------------------------
USE AutoParts_DW;
GO

DECLARE @passed INT = 0, @failed INT = 0;

IF EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'dim')
BEGIN PRINT '[PASS] T09 — DW schema [dim] exists'; SET @passed += 1; END
ELSE
BEGIN PRINT '[FAIL] T09 — DW schema [dim] NOT found'; SET @failed += 1; END

IF EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'fact')
BEGIN PRINT '[PASS] T10 — DW schema [fact] exists'; SET @passed += 1; END
ELSE
BEGIN PRINT '[FAIL] T10 — DW schema [fact] NOT found'; SET @failed += 1; END

IF EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'meta')
BEGIN PRINT '[PASS] T11 — DW schema [meta] exists'; SET @passed += 1; END
ELSE
BEGIN PRINT '[FAIL] T11 — DW schema [meta] NOT found'; SET @failed += 1; END

-- LoadLog table structure
IF EXISTS (
    SELECT 1 FROM sys.tables t
    JOIN sys.schemas s ON t.schema_id = s.schema_id
    WHERE s.name = 'meta' AND t.name = 'LoadLog'
)
BEGIN PRINT '[PASS] T12 — meta.LoadLog table exists'; SET @passed += 1; END
ELSE
BEGIN PRINT '[FAIL] T12 — meta.LoadLog table NOT found'; SET @failed += 1; END

-- LoadLog column checks
IF EXISTS (SELECT 1 FROM sys.columns c
           JOIN sys.tables t ON c.object_id = t.object_id
           JOIN sys.schemas s ON t.schema_id = s.schema_id
           WHERE s.name='meta' AND t.name='LoadLog' AND c.name='BatchID')
BEGIN PRINT '[PASS] T13 — LoadLog.BatchID column exists'; SET @passed += 1; END
ELSE
BEGIN PRINT '[FAIL] T13 — LoadLog.BatchID column NOT found'; SET @failed += 1; END

IF EXISTS (SELECT 1 FROM sys.columns c
           JOIN sys.tables t ON c.object_id = t.object_id
           JOIN sys.schemas s ON t.schema_id = s.schema_id
           WHERE s.name='meta' AND t.name='LoadLog' AND c.name='Status')
BEGIN PRINT '[PASS] T14 — LoadLog.Status column exists'; SET @passed += 1; END
ELSE
BEGIN PRINT '[FAIL] T14 — LoadLog.Status column NOT found'; SET @failed += 1; END

-- LoadLog primary key check
IF EXISTS (
    SELECT 1 FROM sys.indexes i
    JOIN sys.tables t  ON i.object_id = t.object_id
    JOIN sys.schemas s ON t.schema_id = s.schema_id
    WHERE s.name = 'meta' AND t.name = 'LoadLog'
    AND i.is_primary_key = 1
)
BEGIN PRINT '[PASS] T15 — LoadLog has a primary key'; SET @passed += 1; END
ELSE
BEGIN PRINT '[FAIL] T15 — LoadLog primary key NOT found'; SET @failed += 1; END

-- LoadLog: verify IDENTITY column exists
IF EXISTS (
    SELECT 1 FROM sys.columns c
    JOIN sys.tables t  ON c.object_id = t.object_id
    JOIN sys.schemas s ON t.schema_id = s.schema_id
    WHERE s.name = 'meta' AND t.name = 'LoadLog'
    AND c.name = 'LoadLogID' AND c.is_identity = 1
)
BEGIN PRINT '[PASS] T16 — LoadLog.LoadLogID is IDENTITY'; SET @passed += 1; END
ELSE
BEGIN PRINT '[FAIL] T16 — LoadLog.LoadLogID IDENTITY NOT found'; SET @failed += 1; END

-- Smoke test: insert and retrieve from LoadLog
BEGIN TRY
    INSERT INTO meta.LoadLog (TableName, Status)
    VALUES ('TEST_RUN', 'Running');

    IF EXISTS (SELECT 1 FROM meta.LoadLog WHERE TableName = 'TEST_RUN')
    BEGIN
        PRINT '[PASS] T17 — LoadLog insert + read smoke test';
        SET @passed += 1;
        -- Clean up test row
        DELETE FROM meta.LoadLog WHERE TableName = 'TEST_RUN';
    END
    ELSE
    BEGIN PRINT '[FAIL] T17 — LoadLog insert succeeded but row not found'; SET @failed += 1; END
END TRY
BEGIN CATCH
    PRINT '[FAIL] T17 — LoadLog insert smoke test error: ' + ERROR_MESSAGE();
    SET @failed += 1;
END CATCH

PRINT '========================================';
PRINT CONCAT('Results (DW): ', @passed, ' passed, ', @failed, ' failed');
PRINT '========================================';
GO