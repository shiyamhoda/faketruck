-- ============================================================
-- AutoParts Data Platform
-- Script  : 01_create_ods_db.sql
-- Purpose : Create the Operational Data Store (cleansed layer)
-- Sprint  : 1
-- ============================================================

USE master;
GO

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'AutoParts_ODS')
BEGIN
    CREATE DATABASE AutoParts_ODS
    COLLATE SQL_Latin1_General_CP1_CI_AS;
    PRINT 'AutoParts_ODS created.';
END
ELSE
    PRINT 'AutoParts_ODS already exists — skipped.';
GO

USE AutoParts_ODS;
GO

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'ods')
    EXEC('CREATE SCHEMA ods');
GO

PRINT 'ODS schema created.';
GO