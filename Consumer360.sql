CREATE TABLE Raw_Transactions (
    InvoiceNo VARCHAR(20),
    StockCode VARCHAR(20),
    Description TEXT,
    Quantity INT,
    InvoiceDate TIMESTAMP,
    UnitPrice DECIMAL(10,2),
    CustomerID INT,
    Country VARCHAR(50)
);

SELECT COUNT(*) FROM Raw_Transactions;

SELECT COUNT(*) 
FROM raw_transactions
WHERE CustomerID IS NULL;

SELECT COUNT(*) 
FROM raw_transactions
WHERE Quantity <= 0;

SELECT COUNT(*) 
FROM raw_transactions
WHERE UnitPrice <= 0;

CREATE OR REPLACE VIEW cleaned_transactions AS
SELECT
    InvoiceNo,
    StockCode,
    Description,
    Quantity,
    InvoiceDate,   -- no conversion needed
    UnitPrice,
    CustomerID,
    Country,
    Quantity * UnitPrice AS TotalAmount
FROM raw_transactions
WHERE CustomerID IS NOT NULL
AND Quantity > 0
AND UnitPrice > 0;

SELECT COUNT(*) FROM cleaned_transactions;

CREATE TABLE dim_customer AS
SELECT DISTINCT
    CustomerID,
    Country,
    MIN(InvoiceDate) AS First_Purchase_Date
FROM cleaned_transactions
GROUP BY CustomerID, Country;

CREATE TABLE fact_sales AS
SELECT
    InvoiceNo,
    CustomerID,
    StockCode,
    InvoiceDate,
    Quantity,
    UnitPrice,
    TotalAmount
FROM cleaned_transactions;

SELECT
    CustomerID,
    MIN(InvoiceDate) AS First_Purchase_Date
FROM fact_sales
GROUP BY CustomerID;

CREATE TABLE dim_product AS
SELECT DISTINCT
    StockCode,
    Description
FROM cleaned_transactions;

CREATE INDEX idx_fact_customer ON fact_sales(CustomerID);
CREATE INDEX idx_fact_date ON fact_sales(InvoiceDate);
CREATE INDEX idx_fact_product ON fact_sales(StockCode);

CREATE OR REPLACE VIEW single_customer_view AS
SELECT
    CustomerID,
    MIN(InvoiceDate) AS First_Purchase,
    MAX(InvoiceDate) AS Last_Purchase,
    COUNT(DISTINCT InvoiceNo) AS Frequency,
    SUM(TotalAmount) AS Monetary,
    (CURRENT_DATE - MAX(InvoiceDate)::date) AS Recency_Days
FROM fact_sales
GROUP BY CustomerID;

SELECT * FROM single_customer_view
ORDER BY Monetary DESC
LIMIT 10;

SELECT COUNT(*) FROM single_customer_view;

SELECT MAX(Monetary) FROM single_customer_view;