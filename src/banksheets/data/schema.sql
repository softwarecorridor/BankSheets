PRAGMA foreign_keys = 1;

CREATE TABLE IF NOT EXISTS description (
    description_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS bank_transaction (
    id INTEGER PRIMARY KEY,
    date TEXT,
    amount TEXT,
    description INTEGER,
    FOREIGN KEY(description) REFERENCES description(description_id)
);

CREATE TABLE IF NOT EXISTS potential_transaction (
    id INTEGER PRIMARY KEY,
    date TEXT,
    amount TEXT,
    description INTEGER,
    FOREIGN KEY(description) REFERENCES description(description_id)
);

-- TODO: return just a potential transaction id?
CREATE VIEW IF NOT EXISTS duplicate_view AS
    SELECT pt.date, pt.amount, d.name FROM potential_transaction as pt
    INNER JOIN bank_transaction bt ON bt.date = pt.date AND bt.amount = pt.amount AND bt.description = pt.description
    INNER JOIN description d ON d.description_id = pt.description;
