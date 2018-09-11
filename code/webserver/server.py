from flask import Flask, render_template, redirect, url_for, request, flash
from resourcemanager.mainfunctions import VirtInstance
import os
from time import sleep

app = Flask(__name__)
app.secret_key = os.urandom(16)
libvirt_instance = VirtInstance()


@app.route("/")
def hello_world():
    return redirect(url_for("list_vms"))
    # return render_template('index.html')


@app.route("/list_vms")
def list_vms():
    libvirt_instance.update_dom_dict()
    return render_template("list_vms.html", vm_dict=libvirt_instance.domains)


@app.route("/start/<vm_name>")
def start_vm(vm_name):
    try:
        libvirt_instance.start_domain(dom_name=vm_name)
        flash("VM started successfully", category="success")
    except Exception as e:
        flash(message=str(e), category="warning")
    sleep(2)
    return redirect(request.referrer)


@app.route("/stop/<vm_name>")
def stop_vm(vm_name):
    try:
        libvirt_instance.stop_domain(dom_name=vm_name)
        flash("VM stopped successfully", category="success")
    except Exception as e:
        flash(message=str(e), category="warning")
    sleep(2)
    return redirect(request.referrer)


@app.route("/delete/<vm_name>")
def delete_vm(vm_name):
    try:
        libvirt_instance.delete_domain(dom_name=vm_name)
        flash("VM deleted successfully", category="success")
    except Exception as e:
        flash(message=str(e), category="warning")
    sleep(2)
    return redirect(request.referrer)


@app.route("/create", methods=['GET', 'POST'])
def create_vm():
    if request.method == "GET":
        return render_template("create_vm.html")
    elif request.method == "POST":
        try:
            libvirt_instance.create_domain(dom_name=request.form.get("vm_name"),
                                           num_cpu=request.form.get("cpu_num"),
                                           mem=request.form.get("mem_size"))
            flash("VM created successfully", category="success")
        except Exception as e:
            flash(message=str(e), category="warning")
        return redirect(url_for("list_vms"))
    else:
        return 405


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
