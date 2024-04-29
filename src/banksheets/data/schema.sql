PRAGMA foreign_keys = 1;

CREATE TABLE IF NOT EXISTS description (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS bank_transaction (
    id INTEGER PRIMARY KEY,
    date TEXT,
    amount TEXT,
    description_id INTEGER,
    FOREIGN KEY(description_id) REFERENCES description(id)
);

CREATE TABLE IF NOT EXISTS potential_transaction (
    id INTEGER PRIMARY KEY,
    date TEXT,
    amount TEXT,
    description_id INTEGER,
    FOREIGN KEY(description_id) REFERENCES description(id)
);

CREATE TABLE IF NOT EXISTS description_alias (
    id INTEGER PRIMARY KEY,
    description_id INTEGER UNIQUE NOT NULL,
    name TEXT,
    FOREIGN KEY (description_id) REFERENCES description(id)
);
