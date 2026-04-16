-- ============================================================
-- AutoParts Data Platform
-- Script  : 01_create_staging_db.sql
-- Purpose : Create the Staging database for raw data ingest
-- Sprint  : 1
-- ============================================================

USE master;
GO

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'AutoParts_Staging')
BEGIN
    CREATE DATABASE AutoParts_Staging
    COLLATE SQL_Latin1_General_CP1_CI_AS;
    PRINT 'AutoParts_Staging created.';
END
ELSE
    PRINT 'AutoParts_Staging already exists — skipped.';
GO

USE AutoParts_Staging;
GO

-- Schema for raw ingest (one schema per source channel)
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'pos')
    EXEC('CREATE SCHEMA pos');
GO

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'ecom')
    EXEC('CREATE SCHEMA ecom');
GO

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'inventory')
    EXEC('CREATE SCHEMA inventory');
GO

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'supplier')
    EXEC('CREATE SCHEMA supplier');
GO

PRINT 'Staging schemas created.';
GO