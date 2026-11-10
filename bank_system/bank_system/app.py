import random
from flask import Flask, render_template, request, redirect, session, flash
from bank import Bank, get_connection

app = Flask(__name__)
app.secret_key = "mysecret123"


def current_account():
    """Returns the logged-in customer as a Bank object, or None"""
    if "acc_no" not in session:
        return None
    return Bank.get_account(session["acc_no"])


# ---------- Create account ----------
@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        name = request.form["name"]
        age = int(request.form["age"])
        pin = request.form["pin"]

        if age < 18:
            flash("Minimum age to open an account is 18.")
            return render_template("create.html")
        if not (pin.isdigit() and len(pin) == 4):
            flash("PIN must be exactly 4 digits.")
            return render_template("create.html")

        acc_no = random.randint(10000000, 99999999)
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO accounts (acc_no, name, age, pin) VALUES (:1, :2, :3, :4)",
                (acc_no, name, age, pin)
            )
            conn.commit()
            flash(f"Account created! Your account number is {acc_no}. Please login.")
            return redirect("/login")
        except Exception:
            flash("Something went wrong. Please try again.")
        finally:
            conn.close()
    return render_template("create.html")


# ---------- Login ----------
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        acc_no = request.form["acc_no"]
        pin = request.form["pin"]

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT acc_no FROM accounts WHERE acc_no = :1 AND pin = :2",
                    (acc_no, pin))
        row = cur.fetchone()
        conn.close()

        if row:
            session["acc_no"] = row[0]
            return redirect("/dashboard")
        flash("Wrong account number or PIN.")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------- Dashboard ----------
@app.route("/dashboard")
def dashboard():
    acc = current_account()
    if not acc:
        return redirect("/login")
    return render_template("dashboard.html", acc=acc)


@app.route("/update-age", methods=["POST"])
def update_age():
    acc = current_account()
    if not acc:
        return redirect("/login")
    age = int(request.form["age"])
    if age < 18:
        flash("Age must be 18 or more.")
    else:
        acc.ch_age(age)
        flash("Age updated.")
    return redirect("/dashboard")


# ---------- Deposit ----------
@app.route("/deposit", methods=["GET", "POST"])
def deposit():
    acc = current_account()
    if not acc:
        return redirect("/login")
    if request.method == "POST":
        amount = float(request.form["amount"])
        if amount <= 0:
            flash("Enter an amount greater than 0.")
        else:
            acc.deposit(amount)
            flash(f"Rs. {amount} deposited.")
            return redirect("/dashboard")
    return render_template("money.html", title="Deposit")


# ---------- Withdraw ----------
@app.route("/withdraw", methods=["GET", "POST"])
def withdraw():
    acc = current_account()
    if not acc:
        return redirect("/login")
    if request.method == "POST":
        amount = float(request.form["amount"])
        if amount <= 0:
            flash("Enter an amount greater than 0.")
        elif acc.withdraw(amount):
            flash(f"Rs. {amount} withdrawn.")
            return redirect("/dashboard")
        else:
            flash("Insufficient balance.")
    return render_template("money.html", title="Withdraw")


# ---------- History ----------
@app.route("/history")
def history():
    acc = current_account()
    if not acc:
        return redirect("/login")
    return render_template("history.html", rows=acc.history())


# ---------- Interest calculator (static method) ----------
@app.route("/interest", methods=["GET", "POST"])
def interest():
    if "acc_no" not in session:
        return redirect("/login")
    result = None
    if request.method == "POST":
        p = float(request.form["p"])
        r = float(request.form["r"])
        t = float(request.form["t"])
        result = Bank.calc_interest(p, r, t)
    return render_template("interest.html", result=result)


# ---------- Bank info (class methods) ----------
@app.route("/bank-info", methods=["GET", "POST"])
def bank_info():
    if "acc_no" not in session:
        return redirect("/login")
    if request.method == "POST":
        Bank.ch_loc(request.form["loc"])
        flash("Branch location changed.")
    name, loc, ifsc = Bank.bank_details()
    return render_template("bankinfo.html", name=name, loc=loc, ifsc=ifsc)


if __name__ == "__main__":
    app.run(debug=True)
