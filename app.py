from flask import Flask, render_template_string, request, redirect, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = False  
app.config["PERMANENT_SESSION_LIFETIME"] = 1800 
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Donor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    blood_group = db.Column(db.String(10), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(100), nullable=False)


css = """
<style>
body {
  margin: 0;
  font-family: Arial, sans-serif;
  background: url('https://img.freepik.com/free-vector/medical-healthcare-red-background-with-heartbeat_1017-23663.jpg') no-repeat center center fixed;
  background-size: cover;
  color: white;
}
.navbar {
  background: #444;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 30px;
}
.navbar .logo {
  display: flex;
  align-items: center;
  font-size: 22px;
  font-weight: bold;
  color: #ff0033;
  cursor: pointer;
}
.navbar .logo img {
  width: 40px;
  height: 40px;
  margin-right: 10px;
}
.navbar .nav-links {
  display: flex;
  gap: 25px;
}
.navbar .nav-links a {
  color: white;
  text-decoration: none;
  font-weight: bold;
}
.navbar .nav-links a:hover { text-decoration: underline; }
.content {
  text-align: center;
  margin-top: 100px;
}
.content h1 {
  font-size: 40px;
  text-shadow: 2px 2px 5px black;
}
.content p {
  font-size: 20px;
  color: #eee;
  text-shadow: 1px 1px 4px black;
}
.form-container {
  background: rgba(0,0,0,0.85);
  padding: 30px;
  border-radius: 12px;
  width: 400px;
  margin: 40px auto;
  color: white;
}
.form-container h2 { text-align:center; margin-bottom:20px; }
.form-container input, .form-container select {
  width: 100%;
  padding: 12px;
  margin: 8px 0;
  border-radius: 6px;
  border: none;
}
.form-container button {
  width: 100%;
  padding: 12px;
  background: #ff0033;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.form-container button:hover { background: #cc0022; }
.dashboard {
  text-align: center;
  margin-top: 100px;
}
.dashboard button {
  background: #ff0033;
  color: white;
  padding: 14px 30px;
  margin: 15px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 18px;
}
.dashboard button:hover { background: #cc0022; }
.flash {
  margin: 10px auto;
  width: 400px;
  text-align: center;
  padding: 10px;
  border-radius: 6px;
}
.flash.success { background: green; color: white; }
.flash.danger { background: red; color: white; }
</style>
"""

navbar = """
<div class="navbar">
  <div class="logo" onclick="window.location.href='/'">
    <img src="https://cdn-icons-png.flaticon.com/512/983/983887.png"> Blood Connect
  </div>
  <div class="nav-links">
    <a href="/">Home</a>
    {% if 'username' not in session %}
      <a href="/signup">Signup</a>
      <a href="/login">Login</a>
    {% else %}
      <a href="/dashboard">Dashboard</a>
      <a href="/logout">Logout</a>
    {% endif %}
    <a href="/contact">Contact</a>
  </div>
</div>
"""

@app.route("/")
def home():
    return render_template_string(css + navbar + """
    <div class="content">
      <h1>Welcome to Blood Connect</h1>
      <p>"Donate Blood, Save Lives – Be a Hero Today!"</p>
    </div>
    """)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm = request.form["confirm"]

        if password != confirm:
            flash("Passwords do not match!", "danger")
        elif User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
        else:
            user = User(username=username, password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            flash("Signup successful! Please login.", "success")
            return redirect("/login")

    return render_template_string(css + navbar + """
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% for category, message in messages %}
        <div class="flash {{category}}">{{ message }}</div>
      {% endfor %}
    {% endwith %}
    <div class="form-container">
      <h2>Signup</h2>
      <form method="post">
        <input type="text" name="username" placeholder="Username" required>
        <input type="password" name="password" placeholder="Password" required>
        <input type="password" name="confirm" placeholder="Confirm Password" required>
        <button type="submit">Signup</button>
      </form>
    </div>
    """)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["username"] = user.username
            flash("Login successful!", "success")
            return redirect("/dashboard")
        else:
            flash("Invalid credentials!", "danger")

    return render_template_string(css + navbar + """
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% for category, message in messages %}
        <div class="flash {{category}}">{{ message }}</div>
      {% endfor %}
    {% endwith %}
    <div class="form-container">
      <h2>Login</h2>
      <form method="post">
        <input type="text" name="username" placeholder="Username" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Login</button>
      </form>
    </div>
    """)


@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect("/login")
    return render_template_string(css + navbar + """
    <div class="dashboard">
      <h2>Welcome, {{session['username']}} </h2>
      <button onclick="window.location.href='/donor'">Register as Donor</button>
      <button onclick="window.location.href='/donors'">View Donors</button>
      <button onclick="window.location.href='/profile'">My Profile</button>
    </div>
    """)


@app.route("/donor", methods=["GET", "POST"])
def donor():
    if "username" not in session:
        return redirect("/login")
    if request.method == "POST":
        existing = Donor.query.filter_by(username=session["username"]).first()
        if existing:
            flash("You have already registered as a donor!", "danger")
            return redirect("/profile")
        donor = Donor(
            name=request.form["name"],
            contact=request.form["contact"],
            blood_group=request.form["blood_group"],
            state=request.form["state"],
            city=request.form["city"],
            username=session["username"],
        )
        db.session.add(donor)
        db.session.commit()
        flash("Donor registered successfully!", "success")
        return redirect("/donors")

    return render_template_string(css + navbar + """
    <div class="form-container">
      <h2>Register as Donor</h2>
      <form method="post">
        <input type="text" name="name" placeholder="Full Name" required>
        <input type="text" name="contact" placeholder="Contact Number" required>
        <select name="blood_group" required>
          <option value="">Select Blood Group</option>
          <option>A+</option><option>A-</option>
          <option>B+</option><option>B-</option>
          <option>AB+</option><option>AB-</option>
          <option>O+</option><option>O-</option>
        </select>
        <input type="text" name="state" placeholder="State" required>
        <input type="text" name="city" placeholder="City" required>
        <button type="submit">Register</button>
      </form>
    </div>
    """)

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "username" not in session:
        return redirect("/login")
    donor = Donor.query.filter_by(username=session["username"]).first()
    if request.method == "POST" and donor:
        donor.name = request.form["name"]
        donor.contact = request.form["contact"]
        donor.blood_group = request.form["blood_group"]
        donor.state = request.form["state"]
        donor.city = request.form["city"]
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect("/profile")

    return render_template_string(css + navbar + """
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% for category, message in messages %}
        <div class="flash {{category}}">{{ message }}</div>
      {% endfor %}
    {% endwith %}
    <div class="form-container">
      <h2>My Profile</h2>
      {% if donor %}
      <form method="post">
        <input type="text" name="name" value="{{donor.name}}" required>
        <input type="text" name="contact" value="{{donor.contact}}" required>
        <select name="blood_group" required>
          <option {{'selected' if donor.blood_group=='A+'}}>A+</option>
          <option {{'selected' if donor.blood_group=='A-'}}>A-</option>
          <option {{'selected' if donor.blood_group=='B+'}}>B+</option>
          <option {{'selected' if donor.blood_group=='B-'}}>B-</option>
          <option {{'selected' if donor.blood_group=='AB+'}}>AB+</option>
          <option {{'selected' if donor.blood_group=='AB-'}}>AB-</option>
          <option {{'selected' if donor.blood_group=='O+'}}>O+</option>
          <option {{'selected' if donor.blood_group=='O-'}}>O-</option>
        </select>
        <input type="text" name="state" value="{{donor.state}}" required>
        <input type="text" name="city" value="{{donor.city}}" required>
        <button type="submit">Update</button>
      </form>
      {% else %}
      <p style="text-align:center; color:yellow;">You are not registered as a donor yet.</p>
      <button onclick="window.location.href='/donor'">Register Now</button>
      {% endif %}
    </div>
    """, donor=donor)


@app.route("/donors", methods=["GET", "POST"])
def donors():
    if "username" not in session:
        return redirect("/login")

    blood_group = request.form.get("blood_group") if request.method == "POST" else None
    state = request.form.get("state") if request.method == "POST" else None
    city = request.form.get("city") if request.method == "POST" else None

    query = Donor.query
    if blood_group:
        query = query.filter_by(blood_group=blood_group)
    if state:
        query = query.filter(Donor.state.ilike(f"%{state}%"))
    if city:
        query = query.filter(Donor.city.ilike(f"%{city}%"))

    donor_list = query.all()
    items = "".join([f"<li>{d.name} - {d.blood_group} - {d.contact} - {d.state}, {d.city}</li>" for d in donor_list])

    return render_template_string(css + navbar + f"""
    <div class="form-container">
      <h2>Search Donors</h2>
      <form method="post">
        <select name="blood_group">
          <option value="">Select Blood Group</option>
          <option>A+</option><option>A-</option>
          <option>B+</option><option>B-</option>
          <option>AB+</option><option>AB-</option>
          <option>O+</option><option>O-</option>
        </select>
        <input type="text" name="state" placeholder="Enter State">
        <input type="text" name="city" placeholder="Enter City">
        <button type="submit">Search</button>
      </form>
      <ul style="color:white; list-style:none; padding:0;">
        {items if items else "<li>No donors found</li>"}
      </ul>
    </div>
    """)

@app.route("/contact")
def contact():
    return render_template_string(css + navbar + """
    <div class="content">
      <h2>Contact Us</h2>
      <p>Email: support@bloodconnect.com</p>
      <p>Phone: +91-9876543210</p>
    </div>
    """)

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("You have been logged out.", "success")
    return redirect("/")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
