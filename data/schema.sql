CREATE TABLE IF NOT EXISTS descriptions (
    description_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS transactions (
    date TEXT,
    amount TEXT,
    description INTEGER,
    transaction_id TEXT UNIQUE,
    FOREIGN KEY(description) REFERENCES descriptions(description_id)
);

CREATE TABLE IF NOT EXISTS potential_transaction (
    date TEXT,
    amount TEXT,
    description INTEGER,
    pass INTEGER
);

CREATE VIEW IF NOT EXISTS duplicate_transactions AS
SELECT DISTINCT
    pt.date AS potential_date,
    pt.amount AS potential_amount,
    pt.description AS potential_description,
    t.date AS actual_date,
    t.amount AS actual_amount,
    t.description AS actual_description
FROM
    transactions T
INNER JOIN
    potential_transaction pt
ON
    potential_date = actual_date
	AND potential_amount = actual_amount
    AND potential_description = actual_description
