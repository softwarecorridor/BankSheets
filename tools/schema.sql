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

