import os
import bcrypt
from datetime import datetime
from flask import (
    Flask,
    flash,
    render_template,
    request,
    redirect,
    session as flask_session,
    url_for,
)
from pydantic import BaseModel
from database import get_user_by_username, create_user
from sqlmodel import Session

app = Flask("Analyze Face")
app.secret_key = "my secret key"
app.config["UPLOAD_FOLDER"] = "./uploads"
app.config["ALLOWED_EXTENSION"] = {"png", "jpg", "jpeg"}


class RegisterModel(BaseModel):
    first_name: str
    last_name: str
    email: str
    username: str
    age: int
    country: str
    city: str
    password: str
    confirm_password: str
    join_time: str


class LoginModel(BaseModel):
    username: str
    password: str


def allowed_file(filename):
    return True


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        try:
            login_model = LoginModel(
                username=request.form["username"], password=request.form["password"]
            )
        except:
            flash("Type error", "danger")
            return redirect(url_for("login"))

        user = get_user_by_username(login_model.username)

        if user:
            if bcrypt.checkpw(
                login_model.password.encode("utf-8"), user.password.encode("utf-8")
            ):
                flask_session["user_id"] = user.id
                return redirect(url_for("upload"))
            else:
                flash("Password is incorrect", "danger")
                return redirect(url_for("login"))
        else:
            flash("Username is incorrect", "danger")
            return redirect(url_for("login"))


@app.route("/logout")
def logout():
    flask_session.pop("user_id")
    return redirect(url_for("index"))


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if flask_session.get("user_id"):
        flash("Welcome, you are logged in", "success")
        if request.method == "GET":
            return render_template("upload.html")

        elif request.method == "POST":
            my_image = request.files["file"]
            if my_image.filename == "":
                return redirect(url_for("upload"))
            else:
                if my_image and allowed_file(my_image.filename):
                    save_path = os.path.join(
                        app.config["UPLOAD_FOLDER"], my_image.filename
                    )
                    my_image.save(save_path)
                    result = DeepFace.analyze(img_path=save_path, actions=["age"])

                return render_template("result.html", age=result[0]["age"])

    else:
        return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        try:
            register_data = RegisterModel(
                first_name=request.form["first_name"],
                last_name=request.form["last_name"],
                email=request.form["email"],
                username=request.form["username"],
                age=request.form["age"],
                country=request.form["country"],
                city=request.form["city"],
                password=request.form["password"],
                confirm_password=request.form["confirm_password"],
                join_time=str(datetime.now()),
            )
        except:
            flash("Type error", "danger")
            return redirect(url_for("register"))

        if register_data.password != register_data.confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for("register"))

        hashed_password = bcrypt.hashpw(
            register_data.password.encode("utf-8"), bcrypt.gensalt()
        )

        user = get_user_by_username(register_data.username)

        if not user:
            create_user(
                first_name=register_data.first_name,
                last_name=register_data.last_name,
                email=register_data.email,
                username=register_data.username,
                age=register_data.age,
                country=register_data.country,
                city=register_data.city,
                password=hashed_password.decode("utf-8"),
                join_time=str(datetime.now()),
            )
            flash("Your register done successfully", "success")
            return redirect(url_for("login"))
        else:
            flash("Username already exist, Try another username", "danger")
            return redirect(url_for("register"))


@app.route("/bmr", methods=["GET", "POST"])
def bmr():
    if request.method == "GET":
        return render_template("bmr.html")
    elif request.method == "POST":
        gender = request.form["gender"]
        weight = float(request.form["weight"])
        height = float(request.form["height"])
        age = int(request.form["age"])
        if gender == "male":
            result = (10 * weight) + (6.25 * height) - (5 * age) + 5
        elif gender == "female":
            result = (10 * weight) + (6.25 * height) - (5 * age) - 16

        return render_template("resultBMR.html", BMR=result)


@app.route("/read-your-mind", methods=["GET", "POST"])
def read_your_mind():
    if request.method == "POST":
        user_number = request.form["number"]

        return redirect(url_for("read_your_mind_result", number=user_number))

    return render_template("read-your-mind.html")


@app.route("/read-your-mind/result")
def read_your_mind_result():
    suggested_number = request.args.get("number")

    return render_template("read-your-mind-result.html", number=suggested_number)


@app.route("/pose-detection")
def pose_detection():
    return render_template("pose-detection.html")


if __name__ == "__main__":
    app.run(debug=True)
