PRAGMA foreign_keys = 1;

CREATE TABLE IF NOT EXISTS description (
    description_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS bank_transaction (
    date TEXT,
    amount TEXT,
    description INTEGER,
    FOREIGN KEY(description) REFERENCES description(description_id)
);

CREATE TABLE IF NOT EXISTS potential_transaction (
    date TEXT,
    amount TEXT,
    description INTEGER,
    FOREIGN KEY(description) REFERENCES description(description_id)
);

CREATE VIEW IF NOT EXISTS duplicate_view AS
    SELECT
        pt.date,
        pt.amount,
        d.name,
        CASE WHEN COUNT(bt.date) > 1 THEN 1 ELSE 0 END AS duplicate_bank,
        CASE WHEN COUNT(pt.date) > 1 THEN 1 ELSE 0 END AS duplicate_potential
    FROM potential_transaction as pt
    LEFT JOIN bank_transaction bt ON bt.date = pt.date AND bt.amount = pt.amount AND bt.description = pt.description
	INNER JOIN description d ON d.description_id = pt.description;
