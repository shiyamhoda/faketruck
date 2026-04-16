-- ============================================================
-- AutoParts Data Platform
-- Script  : 01_create_dw_db.sql
-- Purpose : Create the Data Warehouse (star schema)
-- Sprint  : 1
-- ============================================================

USE master;
GO

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'AutoParts_DW')
BEGIN
    CREATE DATABASE AutoParts_DW
    COLLATE SQL_Latin1_General_CP1_CI_AS;
    PRINT 'AutoParts_DW created.';
END
ELSE
    PRINT 'AutoParts_DW already exists — skipped.';
GO

USE AutoParts_DW;
GO

-- Separate schemas for clarity
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'dim')
    EXEC('CREATE SCHEMA dim');
GO

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'fact')
    EXEC('CREATE SCHEMA fact');
GO

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'meta')
    EXEC('CREATE SCHEMA meta');
GO

-- ETL load log (used in Sprint 4)
IF NOT EXISTS (SELECT 1 FROM sys.tables t
               JOIN sys.schemas s ON t.schema_id = s.schema_id
               WHERE s.name = 'meta' AND t.name = 'LoadLog')
BEGIN
    CREATE TABLE meta.LoadLog (
        LoadLogID    INT IDENTITY(1,1) PRIMARY KEY,
        BatchID      UNIQUEIDENTIFIER NOT NULL DEFAULT NEWID(),
        TableName    NVARCHAR(128)    NOT NULL,
        LoadStart    DATETIME2        NOT NULL DEFAULT SYSDATETIME(),
        LoadEnd      DATETIME2        NULL,
        RowsInserted INT              NULL,
        RowsUpdated  INT              NULL,
        Status       NVARCHAR(20)     NOT NULL DEFAULT 'Running',
        ErrorMessage NVARCHAR(MAX)    NULL
    );
    PRINT 'meta.LoadLog created.';
END
GO

PRINT 'DW schemas and LoadLog ready.';
GO