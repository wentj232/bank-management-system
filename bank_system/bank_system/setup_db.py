import bank

conn = bank.get_connection()
cur = conn.cursor()

statements = [
    """CREATE TABLE accounts (
        acc_no   NUMBER PRIMARY KEY,
        name     VARCHAR2(100) NOT NULL,
        age      NUMBER(3) NOT NULL,
        pin      VARCHAR2(4) NOT NULL,
        balance  NUMBER(12,2) DEFAULT 0
    )""",
    "CREATE SEQUENCE txn_seq START WITH 1 INCREMENT BY 1",
    """CREATE TABLE transactions (
        txn_id         NUMBER PRIMARY KEY,
        acc_no         NUMBER REFERENCES accounts(acc_no),
        txn_type       VARCHAR2(10),
        amount         NUMBER(12,2),
        balance_after  NUMBER(12,2),
        txn_date       DATE DEFAULT SYSDATE
    )""",
]

for sql in statements:
    name = " ".join(sql.split()[1:3])
    try:
        cur.execute(sql)
        print("CREATED:", name)
    except Exception as e:
        print("SKIPPED:", name, "->", str(e).strip().splitlines()[0])

try:
    cur.execute("""INSERT INTO accounts (acc_no, name, age, pin, balance)
                   VALUES (10000001, 'Test User', 25, '1234', 5000)""")
    conn.commit()
    print("CREATED: test account 10000001 / PIN 1234")
except Exception as e:
    print("SKIPPED: test account ->", str(e).strip().splitlines()[0])

cur.execute("SELECT user FROM dual")
print("Connected as:", cur.fetchone()[0])
cur.execute("SELECT table_name FROM user_tables")
print("Tables I can see:", [r[0] for r in cur.fetchall()])
conn.close()