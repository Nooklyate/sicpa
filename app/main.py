import os, gc
from flask import Flask, request, redirect, url_for, abort, flash, session, escape, jsonify, abort, make_response
from flask.ext.httpauth import HTTPBasicAuth
from werkzeug.utils import secure_filename
from functools import wraps
from flask import render_template
from flask import send_from_directory
from flask import send_file
from settings import APP_STATIC,APP_UPLOADS,APP_CACHE
import pwshort

####
# Setup parameters
####

UPLOAD_FOLDER = APP_UPLOADS
ALLOWED_EXTENSIONS = set(['txt','csv','zip'])
CACHE_FOLDER=APP_CACHE
STATIC_FOLDER=APP_STATIC

f=open(os.path.join(APP_CACHE, '.un'),'r')
uname=f.readline()
f=open(os.path.join(APP_CACHE, '.pw'),'r')
pw=f.readline()

json_out=[]
auth=HTTPBasicAuth()

####
# The app
####
app = Flask(__name__)

#configure logins
f=open(os.path.join(APP_CACHE, '.key'),'r')
app.config['SECRET_KEY'] = f.readline()
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'username' in session:
            return f(*args, **kwargs)
        else:
            flash("ERROR: You need to login first")
            return redirect(url_for('login'))

    return wrap

#configure uploads
enctype="multipart/form-data"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
@app.route('/home/')
def home(name=None):
    if 'username' in session:
        return redirect(url_for('start_page'))

    return redirect(url_for('login'))

@app.route('/thanks')
def thanks(name=None):
    return render_template('thanks.html', name=name)

#user login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != uname or request.form['password'] != pw:
            error = 'Invalid Credentials. Please try again.'
        else:
            session['username'] = request.form['username']
            return redirect(url_for('home'))

    session.clear() 
    return render_template('login.html', error=error)

#start page
@app.route('/start', methods=['GET', 'POST'])
@login_required
def start_page():
    return render_template('start.html')


#file upload page
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file_maintenance' not in request.files or 'file_sensor' not in request.files \
				or 'file_production' not in request.files or 'file_incidents' not in request.files:
            flash('ERROR: No file part')
            return redirect(request.url)
        file_maintenance = request.files['file_maintenance']
        file_sensor = request.files['file_sensor']
        file_production = request.files['file_production']
        file_incidents = request.files['file_incidents']

        # if user does not select file, browser also
        # submit a empty part without filename
        if file_maintenance.filename == '':
            flash('ERROR: No maintenance file selected')
            return redirect(request.url)
        if file_sensor.filename == '':
            flash('ERROR: No sensor file selected')
            return redirect(request.url)
        if file_production.filename == '':
            flash('ERROR: No production file selected')
            return redirect(request.url)
        if file_incidents.filename == '':
            flash('ERROR: No incidents file selected')
            return redirect(request.url)

        # upload files
        nfiles_uploaded=0
        if file_maintenance and allowed_file(file_maintenance.filename):
            filename = 'maintenance.txt' #secure_filename(file_maintenance.filename)
            file_maintenance.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            nfiles_uploaded+=1
        if file_sensor and allowed_file(file_sensor.filename):
            filename = 'sensor.txt.zip' #secure_filename(file_sensor.filename)
            file_sensor.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            nfiles_uploaded+=1
        if file_production and allowed_file(file_production.filename):
            filename = 'production.txt.zip' #secure_filename(file_production.filename)
            file_production.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            nfiles_uploaded+=1
        if file_incidents and allowed_file(file_incidents.filename):
            filename = 'incidents.txt' #secure_filename(file_incidents.filename)
            file_incidents.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            nfiles_uploaded+=1

        if nfiles_uploaded == 4:
            return redirect(url_for('run_prediction'))
        else:
            flash('ERROR: Files not uploaded properly')
            return redirect(request.url)

    return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    #prints text to screen
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

#run code to predict failures
app.config['CACHE_FOLDER'] = CACHE_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/run_prediction')
@login_required
def run_prediction():

	json_out=pwshort.run_prediction(upload_path=app.config['UPLOAD_FOLDER'],static_path=app.config['STATIC_FOLDER'])

	return redirect(url_for('download'))

#data download methods
@app.route('/download')
@login_required
def download():
	try:
		return render_template('download.html')
	except Exception as e:
		return str(e)

@app.route('/return-file')
@login_required
def return_file():
    try:
        return send_file(os.path.join(app.config['STATIC_FOLDER'], 'output.txt'), attachment_filename='output.txt', as_attachment=True)
    except Exception as e:
        return str(e)

@app.route("/logout/")
@login_required
def logout():
    session.clear() 
    flash("You have been logged out!")
    gc.collect()
    return redirect(url_for('thanks'))

#API methods
@app.route('/pfailure/api/v1.0/predictions', methods=['GET'])
@auth.login_required
def get_predictions():
	json_out=pwshort.get_output_json(os.path.join(app.config['STATIC_FOLDER'], 'output.json'))
	return jsonify({'predictions': json_out})

@app.route('/pfailure/api/v1.0/predictions/<int:pid>', methods=['GET'])
@auth.login_required
def get_prediction(pid):
	json_out=pwshort.get_output_json(os.path.join(app.config['STATIC_FOLDER'], 'output.json'))
	pred = [pred for pred in json_out if pred['id'] == pid]
	if len(pred) == 0:
		abort(404)
	return jsonify({'pred': pred[0]})

#API Security
@auth.get_password
def get_password(username):
	if username == uname:
		return pw
	return None

@auth.error_handler
def unauthorized():
	return make_response(jsonify({'Error': 'Unauthorized access'}), 401)

#Error handling
@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'Error': 'Not found'}), 404)
