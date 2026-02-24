from flask import Flask, render_template, request, redirect, session, url_for
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
from bson.objectid import ObjectId
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Load .env
load_dotenv()

# Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# MongoDB Atlas Connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client["portfolioDB"]
contact_collection = db["contacts"]

# Admin credentials
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


# ======================

# Basic Routes
# ======================
@app.route("/")
def home():
    return render_template('index.html')

@app.route("/about.html")
def about():
    return render_template('about.html')

@app.route("/resume.html")
def resume():
    return render_template('resume.html')

@app.route("/services.html")
def services():
    return render_template('services.html')

@app.route("/project.html")
def project():
    return render_template('project.html')

@app.route("/exploremore.html")
def exploremore():
    return render_template('exploremore.html')

@app.route("/contact.html")
def contact_page():
    return render_template("contact.html")


# ======================
# Contact Form (Mongo + Email)
# ======================

# @app.route("/contact.html", methods=["POST"])
# def contact():

#     name = request.form.get("name")
#     email = request.form.get("email")
#     subject = request.form.get("subject")
#     message = request.form.get("message")

#     # Save to MongoDB
#     contact_collection.insert_one({
#         "name": name,
#         "email": email,
#         "subject": subject,
#         "message": message,
#         "date": datetime.utcnow()
#     })

#     # Email Notification
#     sender = os.getenv("EMAIL_USER")
#     password = os.getenv("EMAIL_PASS")

#     msg = MIMEMultipart()
#     msg["From"] = sender
#     msg["To"] = sender
#     msg["Subject"] = f"New Portfolio Message from {name}"

#     body = f"""
#     Name: {name}
#     Email: {email}
#     Subject: {subject}

#     Message:
#     {message}
#     """

#     msg.attach(MIMEText(body, "plain"))

#     try:
#         server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
#         server.login(sender, password)
#         server.sendmail(sender, sender, msg.as_string())
#         server.quit()
#     except Exception as e:
#         print("Email Error:", e)

#     return "OK"


@app.route("/contact.html", methods=["POST"])
def contact():

    name = request.form.get("name")
    email = request.form.get("email")
    subject = request.form.get("subject")
    message = request.form.get("message")

    # Save to MongoDB
    contact_collection.insert_one({
        "name": name,
        "email": email,
        "subject": subject,
        "message": message,
        "date": datetime.utcnow()
    })

    print("Message saved successfully")

    return redirect("/")


# ======================
# Admin Login
# ======================

@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin/messages")
        else:
            return "Invalid Credentials"

    return render_template("admin_login.html")


# ======================
# Admin Messages Page
# ======================

@app.route("/admin/messages")
def admin_messages():

    if not session.get("admin"):
        return redirect("/admin")

    messages = list(contact_collection.find().sort("date", -1))
    return render_template("admin_messages.html", messages=messages)


# ======================
# Delete Message
# ======================

@app.route("/admin/delete/<id>")
def delete_message(id):

    if not session.get("admin"):
        return redirect("/admin")

    contact_collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("admin_messages"))


# ======================
# Logout
# ======================

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/admin")

if __name__ == '__main__':
    app.run(debug=True)