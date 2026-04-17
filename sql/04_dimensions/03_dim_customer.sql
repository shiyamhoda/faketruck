-- ============================================================
-- AutoParts Data Platform
-- Script  : 03_dim_customer.sql
-- Purpose : DimCustomer — SCD Type 2, includes unknown member
-- Sprint  : 2
-- ============================================================

USE AutoParts_DW;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.tables t
    JOIN sys.schemas s ON t.schema_id = s.schema_id
    WHERE s.name = 'dim' AND t.name = 'DimCustomer'
)
BEGIN
    CREATE TABLE dim.DimCustomer (
        CustomerKey     INT           NOT NULL IDENTITY(1,1),
        CustomerCode    NVARCHAR(50)  NOT NULL,   -- 'UNKNOWN' for walk-ins
        CustomerType    NVARCHAR(20)  NOT NULL,   -- 'Retail','Trade','Fleet','Online'
        -- Personal
        FirstName       NVARCHAR(100) NULL,
        LastName        NVARCHAR(100) NULL,
        CompanyName     NVARCHAR(200) NULL,
        -- Contact
        Email           NVARCHAR(200) NULL,
        Phone           NVARCHAR(30)  NULL,
        -- Address
        Address1        NVARCHAR(200) NULL,
        City            NVARCHAR(100) NULL,
        Province        NVARCHAR(100) NULL,
        PostalCode      NVARCHAR(20)  NULL,
        Country         NVARCHAR(100) NOT NULL DEFAULT 'Canada',
        -- Segmentation
        PriceTier       NVARCHAR(20)  NOT NULL DEFAULT 'Standard', -- Standard/Silver/Gold/Platinum
        CreditLimit     DECIMAL(12,2) NULL,
        PaymentTerms    NVARCHAR(30)  NULL,       -- 'COD','Net30','Net60'
        -- SCD Type 2 tracking
        IsActive        BIT           NOT NULL DEFAULT 1,
        ValidFrom       DATE          NOT NULL DEFAULT CAST(GETDATE() AS DATE),
        ValidTo         DATE          NOT NULL DEFAULT '9999-12-31',
        IsCurrent       BIT           NOT NULL DEFAULT 1,
        -- Audit
        CreatedAt       DATETIME2     NOT NULL DEFAULT SYSDATETIME(),
        UpdatedAt       DATETIME2     NOT NULL DEFAULT SYSDATETIME(),
        CONSTRAINT PK_DimCustomer PRIMARY KEY CLUSTERED (CustomerKey)
    );

    CREATE NONCLUSTERED INDEX IX_DimCustomer_Code
        ON dim.DimCustomer (CustomerCode)
        INCLUDE (CustomerKey, IsCurrent);

    -- Unknown member — walk-in / anonymous customers
    SET IDENTITY_INSERT dim.DimCustomer ON;
    INSERT INTO dim.DimCustomer (
        CustomerKey, CustomerCode, CustomerType,
        FirstName, CompanyName, PriceTier,
        ValidFrom, ValidTo, IsCurrent
    )
    VALUES (
        -1, 'UNKNOWN', 'Retail',
        'Walk-in', 'Anonymous Customer', 'Standard',
        '2000-01-01', '9999-12-31', 1
    );
    SET IDENTITY_INSERT dim.DimCustomer OFF;

    PRINT 'dim.DimCustomer created with unknown member (key=-1).';
END
ELSE
    PRINT 'dim.DimCustomer already exists — skipped.';
GO