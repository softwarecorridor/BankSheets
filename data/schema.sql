PRAGMA foreign_keys = 1;

CREATE TABLE IF NOT EXISTS description (
    description_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS bank_transaction (
    date TEXT,
    amount TEXT,
    description INTEGER,
    transaction_id TEXT UNIQUE,
    FOREIGN KEY(description) REFERENCES description(description_id)
);

CREATE TABLE IF NOT EXISTS potential_transaction (
    date TEXT,
    amount TEXT,
    description INTEGER,
    preserve INTEGER DEFAULT 0 NOT NULL
);

CREATE VIEW IF NOT EXISTS duplicate_transaction AS
SELECT DISTINCT
    pt.date AS potential_date,
    pt.amount AS potential_amount,
    pt.description AS potential_description,
    t.date AS actual_date,
    t.amount AS actual_amount,
    t.description AS actual_description
FROM
    bank_transaction T
INNER JOIN
    potential_transaction pt
ON
    potential_date = actual_date
	AND potential_amount = actual_amount
    AND potential_description = actual_description;
