import os
from flask import Flask
from flask import url_for, render_template, request, redirect, send_from_directory
from werkzeug.utils import secure_filename
import time

import utils


app = Flask('extractor')
app.config['UPLOAD_FOLDER'] = 'uploads'



@app.route('/')
def index():
    return render_template('index.html')



@app.route('/extract/', methods=['GET', 'POST'])
def extraction():

    if request.method != 'POST' or not request.files.get('template'):
        return redirect(url_for('index'))
    
    upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'templates')
    template_id = utils.get_next_id(upload_folder) 
    template_dir = os.path.join(upload_folder, str(template_id))
    
    # create the directory
    os.mkdir(template_dir)

    # save the template file 
    template = request.files.get('template')
    filename = secure_filename(template.filename)
    template.save(os.path.join(template_dir, filename))

    # create img from template file  
    max_page = utils.convert_to_img(template_dir, filename)
    
    return render_template('extractor.html', template_id=template_id, max_page=max_page, page=0)


@app.route('/media/<template_id>')
@app.route('/media/<template_id>/<page>')
def get_media(template_id, page=0):
    upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'templates')
    return send_from_directory(
        upload_folder,
        utils.get_page(upload_folder, template_id, page), 
        as_attachment=True
    )


app.run(debug=True)