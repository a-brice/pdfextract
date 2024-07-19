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


def save_file(media_folder):
    template = request.files['template']

    filename = secure_filename(template.filename)
    filename = ''.join(filename.split('.')[:-1]) + f'_{int(time.time())}'

    u_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'templates', filename + '.pdf')
    
    template.save(u_filepath)
    img_folder = utils.convert_to_img(u_filepath, media_folder, filename)
    return img_folder


@app.route('/extract/', methods=['GET', 'POST'])
@app.route('/extract/<template_id>', methods=['GET'])
@app.route('/extract/<template_id>/<page>', methods=['GET'])
def extraction(template_id=None, page=0):

    media_folder = os.path.join(app.config['MEDIA_FOLDER'], 'templates')

    if request.method == 'POST' and request.files.get('template'):

        img_folder = save_file(media_folder)
        img_path = utils.get_imgpage(img_folder, no_page=0) 


    if request.method == 'GET' and template_id:
        assert utils.is_templateID_valid(template_id, media_folder), 'File not downloaded'
        img_folder = os.path.join(media_folder, template_id)
        img_path = utils.get_imgpage(img_folder, no_page=page)

    
    return render_template('extractor.html', img_path=img_path)


@app.route('/media/<filename>')
def get_media(filename):
    return send_from_directory(
        app.config['MEDIA_FOLDER'], 
        filename, 
        as_attachment=True
    )

app.run(debug=True)