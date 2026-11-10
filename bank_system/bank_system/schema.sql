CREATE SEQUENCE txn_seq START WITH 1 INCREMENT BY 1;

CREATE TABLE transactions (
    txn_id         NUMBER PRIMARY KEY,
    acc_no         NUMBER REFERENCES accounts(acc_no),
    txn_type       VARCHAR2(10),
    amount         NUMBER(12,2),
    balance_after  NUMBER(12,2),
    txn_date       DATE DEFAULT SYSDATE
);

INSERT INTO accounts (acc_no, name, age, pin, balance)
VALUES (10000001, 'Test User', 25, '1234', 5000);

COMMIT;