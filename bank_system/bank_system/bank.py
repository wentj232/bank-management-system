import oracledb

oracledb.init_oracle_client(lib_dir=r"C:\Users\PRADYUMNA\app\oracle\product\11.2.0\server\bin")


def get_connection():
    return oracledb.connect(
        user="system",
        password="password",   
        dsn="localhost:1521/XE"
    )


class Bank:
    # ---------- class variables (same for every customer) ----------
    bname = 'SBI'
    loc = 'BBSR'
    ifsc = 'SBIN000'

    # ---------- constructor ----------
    def __init__(self, acc_no, name, age, balance):
        self.acc_no = acc_no
        self.name = name
        self.age = age
        self.balance = balance

    # ---------- instance methods ----------
    def customer_details(self):
        return f"{self.name}, {self.age}, {self.ifsc}"

    def ch_age(self, age):
        self.age = age
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE accounts SET age = :1 WHERE acc_no = :2",
                    (age, self.acc_no))
        conn.commit()
        conn.close()

    def deposit(self, amount):
        self.balance += amount
        self.save_transaction("DEPOSIT", amount)

    def withdraw(self, amount):
        if amount > self.balance:
            return False
        self.balance -= amount
        self.save_transaction("WITHDRAW", amount)
        return True

    def save_transaction(self, txn_type, amount):
        conn = get_connection()
        cur = conn.cursor()
        # both statements are saved together with one commit
        cur.execute("UPDATE accounts SET balance = :1 WHERE acc_no = :2",
                    (self.balance, self.acc_no))
        cur.execute("""INSERT INTO transactions (txn_id, acc_no, txn_type, amount, balance_after)
                       VALUES (txn_seq.NEXTVAL, :1, :2, :3, :4)""",
                    (self.acc_no, txn_type, amount, self.balance))
        conn.commit()
        conn.close()

    def history(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""SELECT txn_date, txn_type, amount, balance_after
                       FROM transactions WHERE acc_no = :1
                       ORDER BY txn_id DESC""", (self.acc_no,))
        rows = cur.fetchall()
        conn.close()
        return rows

    # ---- class methods ----
    @classmethod
    def bank_details(cls):
        return cls.bname, cls.loc, cls.ifsc

    @classmethod
    def ch_loc(cls, new):
        cls.loc = new

    @classmethod
    def get_account(cls, acc_no):
        """Reads a customer from the database and returns a Bank object"""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT name, age, balance FROM accounts WHERE acc_no = :1",
                    (acc_no,))
        row = cur.fetchone()
        conn.close()
        if row:
            return cls(acc_no, row[0], row[1], row[2])
        return None

    # ---------- static method ----------
    @staticmethod
    def calc_interest(p, r, t):
        return p * r * t / 100