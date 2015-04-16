CREATE TABLE tweets3(
       id INT PRIMARY KEY NOT NULL,
       tweet VARCHAR(140),
       posted_by VARCHAR(100),
       timestamp DATETIME,
       label VARCHAR(15),
       positive REAL,
       negative REAL,
       neutral REAL,
       confidence REAL,
       candidate VARCHAR(20));
