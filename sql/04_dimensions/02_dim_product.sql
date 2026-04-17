-- ============================================================
-- AutoParts Data Platform
-- Script  : 02_dim_product.sql
-- Purpose : DimProduct — SCD Type 2 product/part dimension
-- Sprint  : 2
-- ============================================================

USE AutoParts_DW;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.tables t
    JOIN sys.schemas s ON t.schema_id = s.schema_id
    WHERE s.name = 'dim' AND t.name = 'DimProduct'
)
BEGIN
    CREATE TABLE dim.DimProduct (
        ProductKey          INT           NOT NULL IDENTITY(1,1),
        -- Source
        PartNumber          NVARCHAR(50)  NOT NULL,
        PartDescription     NVARCHAR(255) NOT NULL,
        -- Hierarchy
        Category            NVARCHAR(100) NOT NULL,
        SubCategory         NVARCHAR(100) NOT NULL,
        Brand               NVARCHAR(100) NOT NULL,
        -- Cross-refs
        OEMPartNumber       NVARCHAR(100) NULL,
        SupplierPartNumber  NVARCHAR(100) NULL,
        Barcode             NVARCHAR(50)  NULL,
        -- Pricing (SCD2 — captured per version)
        CostPrice           DECIMAL(12,2) NOT NULL DEFAULT 0,
        ListPrice           DECIMAL(12,2) NOT NULL DEFAULT 0,
        -- Attributes
        UnitOfMeasure       NVARCHAR(20)  NOT NULL DEFAULT 'EA',
        WeightKg            DECIMAL(8,3)  NULL,
        IsOEM               BIT           NOT NULL DEFAULT 0,
        IsHazardous         BIT           NOT NULL DEFAULT 0,
        IsActive            BIT           NOT NULL DEFAULT 1,
        -- SCD Type 2 tracking
        ValidFrom           DATE          NOT NULL DEFAULT CAST(GETDATE() AS DATE),
        ValidTo             DATE          NOT NULL DEFAULT '9999-12-31',
        IsCurrent           BIT           NOT NULL DEFAULT 1,
        -- Audit
        CreatedAt           DATETIME2     NOT NULL DEFAULT SYSDATETIME(),
        UpdatedAt           DATETIME2     NOT NULL DEFAULT SYSDATETIME(),
        CONSTRAINT PK_DimProduct PRIMARY KEY CLUSTERED (ProductKey)
    );

    CREATE NONCLUSTERED INDEX IX_DimProduct_PartNumber
        ON dim.DimProduct (PartNumber)
        INCLUDE (ProductKey, IsCurrent);

    CREATE NONCLUSTERED INDEX IX_DimProduct_Category
        ON dim.DimProduct (Category, SubCategory);

    PRINT 'dim.DimProduct created.';
END
ELSE
    PRINT 'dim.DimProduct already exists — skipped.';
GO