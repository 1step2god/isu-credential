import json
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, \
        login_required, login_user, current_user, logout_user
from flask_cors import CORS
from flask_moment import Moment
from apps.tangle import write_data_to_tangle
from apps.findmessages import findmessages
from datetime import datetime

app = Flask(__name__)
CORS(app)
moment= Moment(app)

app.config['SECRET_KEY'] = 'isu2001njcndj'

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'

class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    user = User()
    user.id = username

    return user

# index page
@app.route("/")
def index():
    return render_template('index.html')

def index():
    return render_template('index.html', current_time=datetime.utcnow())

@app.route("/certificate_list")
def certificate_list():
    # Credentials that push to blockchain already
    f = open("static/history.txt", "r")
    content = f.readlines()
    f.close()

    list_content = []
    for obj in content:
        try:
            data = findmessages(obj)
            data_json = {"status":0}
            data_json = json.loads(data)
            hash_url = "https://thetangle.org/bundle/" + obj.rstrip()
            data_json["hash"] = hash_url
            data_json = {"status":1}
        except:
            pass

        list_content.append(data_json)

    # Credentials that not push to blockchain yet
    list_experience = []
    fb = open("static/experience.txt", "r")
    list_raw = fb.readlines()
    fb.close()

    for obj in list_raw:
        print("Hello " + str(obj))
        data_json = json.loads(obj)
        list_experience.append(data_json)

    return render_template('Certificate_list.html', title = list_content, \
            list_experience = list_experience)

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('sign_up.html')
    else:
        # Save to history
        form_content = request.form
        fp = open("static/accounts.txt", "a")
        fp.write(json.dumps(form_content) + "\n")
        fp.close()

    return redirect(url_for("signin"))

@app.route("/signin", methods=['GET', 'POST'])
def signin():
    if request.method == 'GET':
        return render_template('sign_in.html')
    else:
        user = User()
        form_content = request.form
        
        f = open("static/accounts.txt", "r")
        list_content = f.read().splitlines()
        f.close()

        for obj in list_content:
            obj_json = json.loads(obj)
            if obj_json["account"] == form_content["account"] and \
                    obj_json["password"] == form_content["password"]:
                    user = User()
                    user.id = form_content["account"]
                    login_user(user, remember = True)
                    
                    return render_template('index.html', username = current_user.id)

        return render_template('index.html')

# Activity information page
@app.route("/activity_info", methods=['GET', 'POST'])
def activity_info():
    if request.method == 'GET':
        return render_template('ActivityInformation.html')
    else:
        form_content = request.form
        fp = open("static/activities.txt", "a")
        fp.write(json.dumps(form_content) + "\n")
        fp.close()
        return redirect(url_for("activity_info"))

# Write form data to blockchain
@app.route("/write_data", methods=['GET', 'POST'])
def write_data():
    if request.method == 'POST':
        form_content = request.form
        result = write_data_to_tangle(form_content)

        # Save to history
        fp = open("static/history.txt", "a")
        fp.write(str(result["bundle"]) + "\n")
        fp.close()

        return redirect(url_for("backend_credential_editor"))

# Page for student
@app.route("/credential_editor", methods=['GET', 'POST'])
def credential_editor():
    if request.method == 'GET':
        list_credential = []
        fp = open("static/activities.txt", "r")
        list_content = fp.readlines()
        fp.close()

        for obj in list_content:
            list_credential.append(json.loads(obj))
        
        return render_template('credential_editor.html', list_credential = list_credential)
    else:
        fp = open("static/experience.txt", "a")
        fp.write(json.dumps(request.form) + "\n")
        fp.close()

        return redirect(url_for("index"))

@app.route("/personal_micro_credit_list")
def personal_micro_credit_list():
    return render_template('personal_micro_credit_list.html')

@app.route("/personal_micro_credit_apply")
def personal_micro_credit_apply():
    return render_template('personal_micro_credit_apply.html')

# Backend for teacher
@app.route("/backend_credential_editor")
def backend_credential_editor():
    return render_template('backend_credential_editor.html')

@app.route("/verify_list")
def verify_list():
    return render_template('verify_list.html')

@app.route("/review_check")
def review_check():
    return render_template('review_check.html')

@app.route("/review_check_url")
def review_check_url():
    return render_template('review_check_url.html')

@app.route("/new_data", methods=['GET', 'POST'])
def new_data():
    if request.method == 'POST':
        fp = open("static/new_data.txt", "a")
        fp.write(str(request.form) + "\n")
        fp.close()

        return str(request.form)

@app.route("/dashboard")
def dashboard():
    f = open("static/history.txt", "r")
    content = f.readlines()
    f.close()

    return render_template('dashboard.html',title=content)


if __name__ == "__main__":
    app.run(debug = True, threaded = True, host = "0.0.0.0", port = 5000)
