from flask import Flask, render_template
from resourcemanager.mainfunctions import VirtInstance

app = Flask(__name__)
libvirt_instance = VirtInstance()


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/list_vms')
def list_vms():
    libvirt_instance.update_dom_dict()
    return render_template('list_vms.html', vm_dict=libvirt_instance.domains)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
