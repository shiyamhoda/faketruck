-- ============================================================
-- AutoParts Data Platform
-- Script  : 04_dim_store.sql
-- Purpose : DimStore — physical and ecommerce store channels
-- Sprint  : 2
-- ============================================================

USE AutoParts_DW;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.tables t
    JOIN sys.schemas s ON t.schema_id = s.schema_id
    WHERE s.name = 'dim' AND t.name = 'DimStore'
)
BEGIN
    CREATE TABLE dim.DimStore (
        StoreKey        INT           NOT NULL IDENTITY(1,1),
        StoreCode       NVARCHAR(20)  NOT NULL,
        StoreName       NVARCHAR(200) NOT NULL,
        StoreType       NVARCHAR(30)  NOT NULL,   -- 'Retail','Warehouse','Ecommerce'
        Channel         NVARCHAR(20)  NOT NULL,   -- 'Physical','Online'
        -- Location (NULL for online)
        Address1        NVARCHAR(200) NULL,
        City            NVARCHAR(100) NULL,
        Province        NVARCHAR(100) NULL,
        PostalCode      NVARCHAR(20)  NULL,
        Country         NVARCHAR(100) NOT NULL DEFAULT 'Canada',
        Phone           NVARCHAR(30)  NULL,
        -- Operations
        ManagerName     NVARCHAR(200) NULL,
        OpenDate        DATE          NULL,
        CloseDate       DATE          NULL,
        SquareFootage   INT           NULL,
        -- Hierarchy (for multi-region reporting)
        Region          NVARCHAR(100) NULL,
        District        NVARCHAR(100) NULL,
        IsActive        BIT           NOT NULL DEFAULT 1,
        -- Audit
        CreatedAt       DATETIME2     NOT NULL DEFAULT SYSDATETIME(),
        UpdatedAt       DATETIME2     NOT NULL DEFAULT SYSDATETIME(),
        CONSTRAINT PK_DimStore PRIMARY KEY CLUSTERED (StoreKey)
    );

    CREATE UNIQUE NONCLUSTERED INDEX IX_DimStore_Code
        ON dim.DimStore (StoreCode);

    PRINT 'dim.DimStore created.';
END
ELSE
    PRINT 'dim.DimStore already exists — skipped.';
GO