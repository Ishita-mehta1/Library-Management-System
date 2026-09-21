from flask import Flask, render_template, request, redirect, session
from datetime import datetime, timedelta
import json, os
app = Flask(__name__)
app.secret_key = "library_secret_key"
USERNAME ="admin"
PASSWORD ="admin123"
DATA_FILE = "library_data.json"
books = []
members = []
loans = []

def save_data():
    data = {
        "books": books,
        "members": members,
        "loans": loans
    }

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_data():

    global books, members, loans

    if os.path.exists(DATA_FILE):

        with open(DATA_FILE, "r") as f:

            data = json.load(f)

            books = data.get("books", [])
            members = data.get("members", [])
            loans = data.get("loans", [])


load_data()


@app.route("/books")
def books_page():

    return render_template(
        "books.html",
        books=books
    )


@app.route("/add_book", methods=["POST"])
def add_book():

    books.append({
        "id": len(books)+1,
        "title": request.form["title"],
        "price": float(request.form["price"]),
        "copies": int(request.form["copies"]),
        "ebook": request.form["ebook"]
    })

    save_data()

    return redirect("/books")


@app.route("/delete_book/<int:id>")
def delete_book(id):

    global books

    books = [b for b in books if b["id"] != id]

    save_data()

    return redirect("/books")


@app.route("/members")
def members_page():

    return render_template(
        "members.html",
        members=members
    )


@app.route("/add_member", methods=["POST"])
def add_member():

    members.append({
        "id": len(members)+1,
        "name": request.form["name"],
        "email": request.form["email"],
        "phone": request.form["phone"]
    })

    save_data()

    return redirect("/members")


@app.route("/delete_member/<int:id>")
def delete_member(id):

    global members

    members = [m for m in members if m["id"] != id]

    save_data()

    return redirect("/members")

@app.route("/issue")
def issue_page():

    return render_template(
        "issue_book.html",
        books=books,
        members=members
    )


@app.route("/issue_book", methods=["POST"])
def issue_book():

    book_id = int(request.form["book_id"])
    member_id = int(request.form["member_id"])

    # Check book availability
    for book in books:

        if book["id"] == book_id:

            if book["copies"] <= 0:
                return "Book is not available"

            # Reduce available copies
            book["copies"] -= 1
            break

    issue_date = datetime.now()
    due_date = issue_date + timedelta(days=7)

    loans.append({
        "id": len(loans) + 1,
        "book_id": book_id,
        "member_id": member_id,
        "issue_date": str(issue_date),
        "due_date": str(due_date),
        "return_date": None
    })

    save_data()

    return redirect("/")
@app.route("/return")
def return_page():
    active_loans = []

    for loan in loans:
        if not loan.get("return_date"):
            active_loans.append(loan)

    return render_template("return_book.html", loans=active_loans)
@app.route("/return_book/<int:id>")
def return_book(id):

    for loan in loans:

        if loan["id"] == id and not loan.get("return_date"):

            loan["return_date"] = str(datetime.now())

            book_id = loan["book_id"]

            for book in books:
                if book["id"] == book_id:
                    book["copies"] += 1
                    break

            break

    save_data()
    return redirect("/return")


@app.route("/elibrary")
def elibrary():

    return render_template(
        "elibrary.html",
        books=books
    )
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == USERNAME and password == PASSWORD:

            session["user"] = username

            return redirect("/")

        return "Invalid Username or Password"

    return render_template("login.html")
@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/login")
@app.route("/")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        books=books,
        members=members,
        loans=loans
    )
if __name__ == "__main__":
    app.run(debug=True)