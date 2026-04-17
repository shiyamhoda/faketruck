-- ============================================================
-- AutoParts Data Platform
-- Script  : 05_dim_supplier.sql
-- Purpose : DimSupplier — parts suppliers and distributors
-- Sprint  : 2
-- ============================================================

USE AutoParts_DW;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.tables t
    JOIN sys.schemas s ON t.schema_id = s.schema_id
    WHERE s.name = 'dim' AND t.name = 'DimSupplier'
)
BEGIN
    CREATE TABLE dim.DimSupplier (
        SupplierKey     INT           NOT NULL IDENTITY(1,1),
        SupplierCode    NVARCHAR(20)  NOT NULL,
        SupplierName    NVARCHAR(200) NOT NULL,
        SupplierType    NVARCHAR(30)  NOT NULL DEFAULT 'Distributor', -- OEM/Distributor/Importer
        -- Contact
        ContactName     NVARCHAR(200) NULL,
        Email           NVARCHAR(200) NULL,
        Phone           NVARCHAR(30)  NULL,
        Website         NVARCHAR(200) NULL,
        -- Address
        Address1        NVARCHAR(200) NULL,
        City            NVARCHAR(100) NULL,
        Province        NVARCHAR(100) NULL,
        PostalCode      NVARCHAR(20)  NULL,
        Country         NVARCHAR(100) NOT NULL DEFAULT 'Canada',
        -- Commercial
        LeadTimeDays    TINYINT       NOT NULL DEFAULT 3,
        PaymentTerms    NVARCHAR(30)  NOT NULL DEFAULT 'Net30',
        CurrencyCode    NVARCHAR(3)   NOT NULL DEFAULT 'CAD',
        MinOrderValue   DECIMAL(12,2) NULL,
        IsActive        BIT           NOT NULL DEFAULT 1,
        -- Audit
        CreatedAt       DATETIME2     NOT NULL DEFAULT SYSDATETIME(),
        UpdatedAt       DATETIME2     NOT NULL DEFAULT SYSDATETIME(),
        CONSTRAINT PK_DimSupplier PRIMARY KEY CLUSTERED (SupplierKey)
    );

    CREATE UNIQUE NONCLUSTERED INDEX IX_DimSupplier_Code
        ON dim.DimSupplier (SupplierCode);

    PRINT 'dim.DimSupplier created.';
END
ELSE
    PRINT 'dim.DimSupplier already exists — skipped.';
GO