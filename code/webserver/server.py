from flask import Flask, render_template, redirect, url_for, request, flash, session
from resourcemanager.mainfunctions import VirtInstance
import db
import os
from time import sleep
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.secret_key = os.urandom(16)
app.config["DATABASE"] = os.path.dirname(os.path.abspath(__file__))+"/flask.sql"
libvirt_instance = VirtInstance()

if not os.path.isfile(app.config["DATABASE"]):
    db.init_db(app)
    with app.app_context():
        myDB = db.get_db()
        myDB.execute('INSERT INTO user (username, password) VALUES (?, ?)',
                     ("admin", generate_password_hash("admin")))
        myDB.execute('INSERT INTO usrp (id, in_use_on) VALUES (?, ?)',
                     ("0", "-1"))
        myDB.execute('INSERT INTO usrp (id, in_use_on) VALUES (?, ?)',
                     ("1", "-1"))
        myDB.commit()

db.init_app(app)


@app.route("/")
def hello_world():
    if "user_id" not in session:
        return redirect(url_for('login'))

    return redirect(url_for("list_vms"))


@app.route("/login", methods=('GET', 'POST'))
def login():
    if "user_id" in session:
        return redirect(url_for('hello_world'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        myDB = db.get_db()

        error = None
        user = myDB.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['username']
            return redirect(url_for('list_vms'))

        flash(error, "error")

    return render_template('login.html')


@app.route("/logout")
def logout():
    if "user_id" not in session:
        return redirect(url_for('login'))

    session.pop("user_id")
    return redirect(url_for('login'))


@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        myDB = db.get_db()

        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif myDB.execute(
            'SELECT username FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            myDB.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            myDB.commit()
            return redirect(url_for('hello_world'))

        flash(error, "error")

    return render_template('register.html')


@app.route("/list_vms")
def list_vms():
    if "user_id" not in session:
        return redirect(url_for('login'))

    libvirt_instance.update_dom_dict()
    myDB = db.get_db()
    vms = db.get_vms_by_user(myDB, session["user_id"])
    usrps = db.get_free_usrps(myDB)
    vms_dict = {}
    for vm in vms:
        vms_dict[vm] = libvirt_instance.domains[vm]
    return render_template("list_vms.html", vm_dict=vms_dict, usrp_list=usrps)


@app.route("/list_all_vms")
def list_all_vms():
    if ("user_id" not in session) or (session["user_id"] != "admin"):
        return redirect(url_for('list_vms'))
    myDB = db.get_db()
    usrps = db.get_free_usrps(myDB)
    libvirt_instance.update_dom_dict()
    return render_template("list_vms.html", vm_dict=libvirt_instance.domains, usrp_list=usrps)


@app.route("/start/<vm_name>", methods=["POST"])
def start_vm(vm_name):
    if "user_id" not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        usrp = int(request.form['usrp'])
        myDB = db.get_db()
        if usrp in db.get_free_usrps(myDB):
            db.set_usrp(myDB, vm_name, usrp)
            libvirt_instance.attach_usrp(vm_name, usrp_num=usrp)

        try:
            libvirt_instance.start_domain(dom_name=vm_name)
            flash("VM started successfully", category="success")
        except Exception as e:
            flash(message=str(e), category="warning")
        sleep(2)
        return redirect(request.referrer)
    else:
        return 401


@app.route("/stop/<vm_name>")
def stop_vm(vm_name):
    if "user_id" not in session:
        return redirect(url_for('login'))

    try:
        libvirt_instance.stop_domain(dom_name=vm_name)
        myDB = db.get_db()
        db.unset_usrp(myDB, vm_name)
        libvirt_instance.dettach_usrp(vm_name)
        flash("VM stopped successfully", category="success")
    except Exception as e:
        flash(message=str(e), category="warning")
    sleep(2)
    return redirect(request.referrer)


@app.route("/delete/<vm_name>")
def delete_vm(vm_name):
    if "user_id" not in session:
        return redirect(url_for('login'))
    myDB = db.get_db()
    try:
        libvirt_instance.delete_domain(dom_name=vm_name)
        db.remove_vm(myDB, vm_name)
        flash("VM deleted successfully", category="success")
    except Exception as e:
        flash(message=str(e), category="warning")
    sleep(2)
    return redirect(request.referrer)


@app.route("/create", methods=['GET', 'POST'])
def create_vm():
    if "user_id" not in session:
        return redirect(url_for('login'))
    myDB = db.get_db()
    if request.method == "GET":
        return render_template("create_vm.html")
    elif request.method == "POST":
        try:
            dom = libvirt_instance.create_domain(dom_name=request.form.get("vm_name"),
                                                 num_cpu=request.form.get("cpu_num"),
                                                 mem=request.form.get("mem_size"))

            db.reg_domain(myDB, dom.name(), session["user_id"])

            flash("VM created successfully", category="success")
        except Exception as e:
            flash(message=str(e), category="warning")
        return redirect(url_for("list_vms"))
    else:
        return 405


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
