-- ============================================================
-- AutoParts Data Platform
-- Script  : 01_dim_date.sql
-- Purpose : DimDate — date dimension with fiscal calendar
-- Sprint  : 2
-- ============================================================

USE AutoParts_DW;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.tables t
    JOIN sys.schemas s ON t.schema_id = s.schema_id
    WHERE s.name = 'dim' AND t.name = 'DimDate'
)
BEGIN
    CREATE TABLE dim.DimDate (
        DateKey          INT          NOT NULL,   -- YYYYMMDD surrogate
        FullDate         DATE         NOT NULL,
        Year             SMALLINT     NOT NULL,
        Quarter          TINYINT      NOT NULL,
        QuarterName      NVARCHAR(6)  NOT NULL,   -- Q1..Q4
        Month            TINYINT      NOT NULL,
        MonthName        NVARCHAR(12) NOT NULL,
        MonthShort       NVARCHAR(3)  NOT NULL,   -- Jan..Dec
        Week             TINYINT      NOT NULL,   -- ISO week
        DayOfMonth       TINYINT      NOT NULL,
        DayOfWeek        TINYINT      NOT NULL,   -- 1=Mon..7=Sun
        DayName          NVARCHAR(12) NOT NULL,
        DayShort         NVARCHAR(3)  NOT NULL,
        IsWeekend        BIT          NOT NULL DEFAULT 0,
        IsPublicHoliday  BIT          NOT NULL DEFAULT 0,
        HolidayName      NVARCHAR(100) NULL,
        -- Fiscal calendar (Apr–Mar year, adjust as needed)
        FiscalYear       NVARCHAR(9)  NOT NULL,   -- e.g. FY2024-25
        FiscalQuarter    TINYINT      NOT NULL,
        FiscalMonth      TINYINT      NOT NULL,
        YearMonth        INT          NOT NULL,   -- YYYYMM for easy grouping
        YearQuarter      NVARCHAR(7)  NOT NULL,   -- 2024-Q1
        CONSTRAINT PK_DimDate PRIMARY KEY CLUSTERED (DateKey)
    );
    PRINT 'dim.DimDate created.';
END
ELSE
    PRINT 'dim.DimDate already exists — skipped.';
GO