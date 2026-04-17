-- ============================================================
-- AutoParts Data Platform
-- Script  : 01_fact_sales.sql
-- Purpose : Create the Sales fact table for reporting
-- Sprint  : 3
-- ============================================================

USE AutoParts_DW;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.tables t
    JOIN sys.schemas s ON t.schema_id = s.schema_id
    WHERE s.name = 'fact' AND t.name = 'FactSales'
)
BEGIN
    CREATE TABLE fact.FactSales (
        SalesKey          BIGINT        NOT NULL IDENTITY(1,1),
        OrderNumber       NVARCHAR(30)  NOT NULL,
        OrderLineNumber   INT           NOT NULL,
        OrderDateKey      INT           NOT NULL,
        ProductKey        INT           NOT NULL,
        CustomerKey       INT           NOT NULL,
        StoreKey          INT           NOT NULL,
        SupplierKey       INT           NULL,
        Quantity          INT           NOT NULL,
        UnitPrice         DECIMAL(12,2) NOT NULL,
        ExtendedAmount    DECIMAL(12,2) NOT NULL,
        DiscountAmount    DECIMAL(12,2) NOT NULL DEFAULT 0,
        NetSalesAmount    DECIMAL(12,2) NOT NULL,
        TaxAmount         DECIMAL(12,2) NOT NULL DEFAULT 0,
        TotalAmount       DECIMAL(12,2) NOT NULL,
        UnitCost          DECIMAL(12,2) NOT NULL DEFAULT 0,
        TotalCost         DECIMAL(12,2) NOT NULL DEFAULT 0,
        GrossProfitAmount DECIMAL(12,2) NOT NULL DEFAULT 0,
        CreatedAt         DATETIME2     NOT NULL DEFAULT SYSDATETIME(),
        CONSTRAINT PK_FactSales PRIMARY KEY CLUSTERED (SalesKey),
        CONSTRAINT FK_FactSales_OrderDate
            FOREIGN KEY (OrderDateKey) REFERENCES dim.DimDate (DateKey),
        CONSTRAINT FK_FactSales_Product
            FOREIGN KEY (ProductKey) REFERENCES dim.DimProduct (ProductKey),
        CONSTRAINT FK_FactSales_Customer
            FOREIGN KEY (CustomerKey) REFERENCES dim.DimCustomer (CustomerKey),
        CONSTRAINT FK_FactSales_Store
            FOREIGN KEY (StoreKey) REFERENCES dim.DimStore (StoreKey),
        CONSTRAINT FK_FactSales_Supplier
            FOREIGN KEY (SupplierKey) REFERENCES dim.DimSupplier (SupplierKey),
        CONSTRAINT CK_FactSales_Quantity
            CHECK (Quantity > 0),
        CONSTRAINT CK_FactSales_OrderLineNumber
            CHECK (OrderLineNumber > 0)
    );

    CREATE UNIQUE NONCLUSTERED INDEX IX_FactSales_OrderLine
        ON fact.FactSales (OrderNumber, OrderLineNumber);

    CREATE NONCLUSTERED INDEX IX_FactSales_OrderDate
        ON fact.FactSales (OrderDateKey)
        INCLUDE (NetSalesAmount, GrossProfitAmount, Quantity);

    CREATE NONCLUSTERED INDEX IX_FactSales_ProductDate
        ON fact.FactSales (ProductKey, OrderDateKey)
        INCLUDE (NetSalesAmount, Quantity);

    CREATE NONCLUSTERED INDEX IX_FactSales_StoreDate
        ON fact.FactSales (StoreKey, OrderDateKey)
        INCLUDE (NetSalesAmount, GrossProfitAmount);

    PRINT 'fact.FactSales created.';
END
ELSE
    PRINT 'fact.FactSales already exists - skipped.';
GO
