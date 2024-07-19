import os
from flask import Flask
from flask import url_for, render_template, request, redirect, send_from_directory, Response
from werkzeug.utils import secure_filename
import time

import utils
import alignement
import extract
import json

import pandas as pd

import cv2 


# TODO 
### Inclusion et Extraction de JPG/PNG 
### Formatting des apps en 2 parties (partie drawing et partie config file)
### Test unitaires avec la sécurisation de l'app
### Création de l'API 

app = Flask('extractor')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DRAWING_FOLDER'] = os.path.join('uploads', 'by_drawing')
app.config['CONF_FOLDER'] = os.path.join('uploads', 'with_config')

if not os.path.exists(app.config['DRAWING_FOLDER']):
    os.makedirs(app.config['DRAWING_FOLDER'])

if not os.path.exists(app.config['CONF_FOLDER']):
    os.makedirs(app.config['CONF_FOLDER'])


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/template-choice')
def template_choice():
    return render_template('template_choice.html')



@app.route('/draw/', methods=['GET', 'POST'])
def get_drawing():

    if request.method != 'POST' or not request.files.get('template'):
        return redirect(url_for('index'))
    
    sess_id = utils.get_next_id(app.config['DRAWING_FOLDER']) 
    template_dir = os.path.join(app.config['DRAWING_FOLDER'], str(sess_id), 'template_pdf')
    
    # create the directory
    os.makedirs(template_dir)

    # save the template file 
    template = request.files.get('template')
    filename = secure_filename(template.filename)
    template.save(os.path.join(template_dir, filename))

    # create img from template file  
    max_page = utils.convert_to_img(template_dir, filename)
    
    return render_template('drawing.html', sess_id=sess_id, max_page=max_page, page=0)


@app.route('/media/<sess_id>')
@app.route('/media/<sess_id>/<page>')
def get_media(sess_id, page=0):
    upload_folder = os.path.join(app.config['DRAWING_FOLDER'], str(sess_id), 'template_pdf', 'pages')
    return send_from_directory(
        upload_folder,
        utils.get_page(upload_folder, page, False), 
        as_attachment=True
    )

@app.route('/<sess_id>/drawing/save', methods=['POST'])
def save_drawing(sess_id):
    upload_folder = os.path.join(app.config['DRAWING_FOLDER'], str(sess_id))
    filepath = os.path.join(upload_folder, 'drawing.json')

    if not os.path.exists(upload_folder):
        return Response('The sess_id path does not exist', status=400)

    with open(upload_folder + '/drawing.json', 'w') as f:
        drawing = request.json
        drawing = [
            {k:(eval(v) if k in ['page', 'bbox'] else v) for k,v in x.items()} 
            for x in drawing
        ]
        drawing = utils.occurence_dict(drawing)
        json.dump(drawing, f)
        
    
    return Response('OK', status=200)


@app.route('/<sess_id>/drawing/download')
def download_drawing(sess_id):
    upload_folder = os.path.join(app.config['DRAWING_FOLDER'], str(sess_id))
    filepath = os.path.join(upload_folder, 'drawing.json')
    
    if not os.path.exists(filepath):
        return Response('The config file has not be saved', status=400)

    return send_from_directory(
        upload_folder,
        'drawing.json', 
        as_attachment=True
    )


@app.route('/<sess_id>/result/<type>/download')
@app.route('/result/<type>/download')
def download_result(sess_id=None, type='CSV'):
    
    if sess_id is not None:
        upload_folder = os.path.join(app.config['DRAWING_FOLDER'], str(sess_id))
    else:
        sess_id = request.args.get('sess_id')
        assert sess_id != '', 'Session id is mandatory'
        upload_folder = os.path.join(app.config['CONF_FOLDER'], str(sess_id))

    if type == 'CSV':
        filename = 'result.csv'
    else:
        filename = 'result.json'

    if not os.path.exists(os.path.join(upload_folder, filename)):
        return Response('The result file has not be created', status=400)

    return send_from_directory(
        upload_folder,
        filename, 
        as_attachment=True
    )


@app.route('/pdf/<sess_id>/extract')
def get_test_pdf(sess_id):
    return render_template('pdf_to_convert.html', sess_id=sess_id)



@app.route('/extraction/', methods=['POST'])
def extraction():

    if not request.form.get('sess_id') or len(request.files) == 0:
        return Response('Bad request', 400)
    
    sess_id = request.form.get('sess_id')
    upload_folder = os.path.join(app.config['DRAWING_FOLDER'], str(sess_id))
    template_dir = os.path.join(upload_folder, 'template_pdf')
    testdir = os.path.join(upload_folder, 'test_pdf')
    
    if not os.path.exists(testdir):
        os.mkdir(testdir)

    with open(os.path.join(upload_folder, 'drawing.json'), 'r') as json_file:
        drawing = json.load(json_file)

    all_pdf_infos = {}

    for file in request.files.getlist('pdfs[]'):
        filename = secure_filename(file.filename)
        dirname, extension = filename.rsplit('.', 1)
        test_dir = os.path.join(testdir, dirname)

        if extension == 'pdf':
            os.makedirs(test_dir, exist_ok=True)
            file.save(os.path.join(test_dir, filename))
            utils.convert_to_img(test_dir, filename)
            infos = extract_from_pdf(template_dir, test_dir, drawing)
            all_pdf_infos[filename] = infos
        
        elif extension == 'png' or extension == 'jpg':
            file.save(os.path.join(testdir, filename))

        else: 
            raise Exception('Extension file not handled')


    df = pd.DataFrame.from_dict(all_pdf_infos, orient='index')
    df.reset_index().rename(columns={'index': 'File'}).to_csv(
        os.path.join(upload_folder, 'result.csv'), 
        sep=';', 
        index=False
    )
    df.to_json(os.path.join(upload_folder, 'result.json'), orient='index')

    return Response('OK', 200)



def extract_from_pdf(template_dir, testdir, drawing):
    template_dir = os.path.join(template_dir, 'pages')
    test_dir = os.path.join(testdir, 'pages')
        
    pages = set([x['page'] for x in drawing])
    infos = {}

    for no_page in pages:
        start = time.time()
        template_img = utils.get_page(template_dir, no_page)
        test_img = utils.get_page(test_dir, no_page)
        img = alignement.align_to_template(test_img, template_img)
        drawing_page = [x for x in drawing if x['page'] == no_page]
        info, img_show = extract.extract_text(img, drawing_page)
        extract.show_highlighted_img(testdir, no_page, img_show)
        info[f'time_for_page_no_{no_page}(sec)'] = round((time.time() - start), 2)
        infos = dict(**infos, **info)
    
    return infos

@app.route('/file-choice')
def select_files():
   return render_template('file_choice.html') 


@app.route('/with-config/process', methods=['POST'])
def process_files():
    template = request.files.get('template')
    drawing = request.files.get('config')
    test_files = request.files.getlist('test')

    sess_id = utils.get_next_id(app.config['CONF_FOLDER'])

    upload_folder = os.path.join(app.config['CONF_FOLDER'], str(sess_id))
    template_dir = os.path.join(upload_folder, 'template_pdf')
    os.makedirs(template_dir)

    # save and convert to image the template pdf
    template.save(os.path.join(template_dir, secure_filename(template.filename)))
    utils.convert_to_img(template_dir, secure_filename(template.filename))
    
    # save the drawing (config file)
    drawing.save(os.path.join(upload_folder, 'drawing.json'))
    with open(os.path.join(upload_folder, 'drawing.json'), 'r') as json_file:
        drawing = json.load(json_file)
        drawing = utils.occurence_dict(drawing)

    # save all files in directory containing their name and convert them to images
    all_pdf_infos = {}
    for file in test_files:
        filename = secure_filename(file.filename)
        dirname, extension = filename.rsplit('.', 1)
        test_dir = os.path.join(upload_folder, 'test_pdf', dirname)

        if extension == 'pdf':
            os.makedirs(test_dir, exist_ok=True)
            file.save(os.path.join(test_dir, filename))
            utils.convert_to_img(test_dir, filename)
            infos = extract_from_pdf(template_dir, test_dir, drawing)
            all_pdf_infos[filename] = infos
            
        elif extension == 'png' or extension == 'jpg':
            file.save(os.path.join(upload_folder, 'test_pdf', filename))

        else: 
            raise Exception('Extension file not handled')

    df = pd.DataFrame.from_dict(all_pdf_infos, orient='index')
    df.reset_index().rename(columns={'index': 'File'}).to_csv(
        os.path.join(upload_folder, 'result.csv'), 
        sep=';', 
        index=False
    )
    df.to_json(os.path.join(upload_folder, 'result.json'), orient='index')

    return {'sess_id': sess_id}



app.run(debug=True)