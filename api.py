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


app = Flask('extractor')
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'] + '/templates')


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/draw/', methods=['GET', 'POST'])
def get_drawing():

    if request.method != 'POST' or not request.files.get('template'):
        return redirect(url_for('index'))
    
    upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'templates')
    template_id = utils.get_next_id(upload_folder) 
    template_dir = os.path.join(upload_folder, str(template_id), 'template_pdf')
    
    # create the directory
    os.makedirs(template_dir)

    # save the template file 
    template = request.files.get('template')
    filename = secure_filename(template.filename)
    template.save(os.path.join(template_dir, filename))

    # create img from template file  
    max_page = utils.convert_to_img(template_dir, filename)
    
    return render_template('drawing.html', template_id=template_id, max_page=max_page, page=0)


@app.route('/media/<template_id>')
@app.route('/media/<template_id>/<page>')
def get_media(template_id, page=0):
    upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'templates', str(template_id), 'template_pdf', 'pages')
    return send_from_directory(
        upload_folder,
        utils.get_page(upload_folder, page, False), 
        as_attachment=True
    )

@app.route('/<template_id>/drawing/save', methods=['POST'])
def save_drawing(template_id):
    upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'templates', str(template_id))
    filepath = os.path.join(upload_folder, 'drawing.json')

    if not os.path.exists(upload_folder):
        return Response('The template_id path does not exist', status=400)

    with open(upload_folder + '/drawing.json', 'w') as f:
        drawing = request.json
        drawing = [
            {k:(eval(v) if k in ['page', 'bbox'] else v) for k,v in x.items()} 
            for x in drawing
        ]
        drawing = utils.occurence_dict(drawing)
        json.dump(drawing, f)
        
    
    return Response('OK', status=200)


@app.route('/<template_id>/drawing/download')
def download_drawing(template_id):
    upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'templates', str(template_id))
    filepath = os.path.join(upload_folder, 'drawing.json')
    
    if not os.path.exists(filepath):
        return Response('The config file has not be saved', status=400)

    return send_from_directory(
        upload_folder,
        'drawing.json', 
        as_attachment=True
    )


@app.route('/<template_id>/result/<type>/download')
def download_result(template_id, type):
    upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'templates', str(template_id))
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


@app.route('/pdf/<template_id>/extract')
def get_test_pdf(template_id):
    return render_template('pdf_to_convert.html', template_id=template_id)



@app.route('/extraction/', methods=['POST'])
def extraction():

    if len(request.files) > 0 and request.form.get('template_id'):
        template_id = request.form.get('template_id')
        upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'templates', str(template_id), 'test_pdf')
        
        if not os.path.exists(upload_folder):
            os.mkdir(upload_folder)

        dirnames = []

        for file in request.files.getlist('pdfs[]'):
            filename = secure_filename(file.filename)
            dirname, extension = filename.rsplit('.', 1)
            dirnames.append(dirname)

            if extension == 'pdf':
                if not os.path.exists(os.path.join(upload_folder, dirname)):
                    os.mkdir(os.path.join(upload_folder, dirname))
                file.save(os.path.join(upload_folder, dirname, filename))
                utils.convert_to_img(os.path.join(upload_folder, dirname), filename)
            
            elif extension == 'png' or extension == 'jpg':
                file.save(os.path.join(upload_folder, filename))

            else: 
                raise Exception('Extension file not handled')

        all_pdf_infos = {}
    
        for name in dirnames:
            infos = extract_from_pdf(template_id, name)
            all_pdf_infos[name] = infos
        
        result_path = os.path.join(app.config['UPLOAD_FOLDER'], 'templates', str(template_id))
        
        df = pd.DataFrame.from_dict(all_pdf_infos, orient='index')
        df.reset_index().rename(columns={'index': 'File'}).to_csv(
            os.path.join(result_path, 'result.csv'), 
            sep=';', 
            index=False
        )
        df.to_json(os.path.join(result_path, 'result.json'), orient='index')

    return Response('OK', 200)



def extract_from_pdf(template_id, testname):
    dirpath = os.path.join(app.config['UPLOAD_FOLDER'], 'templates', str(template_id))
    template_dir = os.path.join(dirpath, 'template_pdf', 'pages')
    test_dir = os.path.join(dirpath, 'test_pdf', testname, 'pages')
    show_dir = os.path.join(dirpath, 'test_pdf', testname, 'show')
    
    # to debug 
    if not os.path.exists(show_dir):
        os.mkdir(show_dir)


    with open(os.path.join(dirpath, 'drawing.json'), 'r') as json_file:
        drawing = json.load(json_file)
        
    pages = set([x['page'] for x in drawing])
    infos = {}

    for no_page in pages:
        start = time.time()
        template_img = utils.get_page(template_dir, no_page)
        test_img = utils.get_page(test_dir, no_page)
        img = alignement.align_to_template(test_img, template_img)
        drawing_page = [x for x in drawing if x['page'] == no_page]
        info, img_show = extract.extract_text(img, drawing_page)
        cv2.imwrite(show_dir + f'/p{no_page}.png', img_show)
        info[f'time_for_page_no_{no_page}(sec)'] = round((time.time() - start), 2)
        infos = dict(**infos, **info)
    
    return infos


app.run(debug=True)