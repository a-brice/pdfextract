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
import glob
import shutil
import pathlib 


# TODO 
### Test unitaires avec la sécurisation de l'app
### Création de l'API 

app = Flask('extractor')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DRAWING_FOLDER'] = os.path.join('uploads', 'by_drawing')
app.config['TEMP_FOLDER'] = os.path.join('uploads', 'temp')
app.config['CONF_FOLDER'] = os.path.join('uploads', 'with_config')

if not os.path.exists(app.config['DRAWING_FOLDER']):
    os.makedirs(app.config['DRAWING_FOLDER'])

if not os.path.exists(app.config['TEMP_FOLDER']):
    os.makedirs(app.config['TEMP_FOLDER'])

if not os.path.exists(app.config['CONF_FOLDER']):
    os.makedirs(app.config['CONF_FOLDER'])


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/template-choice')
def template_choice():
    return render_template('template_choice.html')



@app.route('/draw/', methods=['GET', 'POST', 'PUT'])
def get_drawing():

    if request.method == 'PUT': 
        dpi = request.form.get('dpi')
        sess_id = request.form.get('sess_id')
        assert dpi and sess_id and dpi.isnumeric() and sess_id.isnumeric(), "either dpi or id is not numeric"
        
        template_dir = os.path.join(app.config['DRAWING_FOLDER'], str(sess_id), 'template_pdf')
        assert os.path.exists(template_dir), "template directory not found"
        
        filenames = [x for x in os.listdir(template_dir) if '.pdf' in x]
        assert len(filenames) != 0, "template does not exist"

        max_page = utils.convert_to_img(template_dir, filenames[0], dpi=int(dpi))

        return Response('OK', 200)
    
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
    dpi = 180
    max_page = utils.convert_to_img(template_dir, filename, dpi=dpi)
    
    return render_template('drawing.html', sess_id=sess_id, max_page=max_page, page=0, dpi=dpi)


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

    with open(filepath, 'w', encoding='utf-8') as f:
        config = request.json
        config['drawing'] = [
            {k:(eval(v) if k in ['page', 'bbox'] else v) for k,v in x.items()} 
            for x in config['drawing']
        ]
        config['drawing'] = utils.occurence_dict(config['drawing'])
        json.dump(config, f)
        
    
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
    if sess_id == 'temp':
        upload_folder = app.config['TEMP_FOLDER']
    elif sess_id is not None:
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


def save_result(dirpath, infos, _1toN=False):
    
    
    with open(os.path.join(dirpath, 'result.json'), 'w', encoding='utf-8') as file:
        json.dump(infos, file, ensure_ascii=False)


    if _1toN:
        json_data = pd.json_normalize(infos, sep='_', max_level=1).to_dict(orient='records')[0]
        df = pd.DataFrame.from_dict(json_data, orient='index')
    else:    
        df = pd.DataFrame.from_dict(infos, orient='index')
    
    df.reset_index().rename(columns={'index': 'File'}).to_csv(
        os.path.join(dirpath, 'result.csv'), 
        sep=';', 
        index=False
    )


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

    with open(os.path.join(upload_folder, 'drawing.json'), 'r', encoding='utf-8') as json_file:
        config = json.load(json_file)
        dpi = config['dpi']
        drawing = config['drawing']

    all_pdf_infos = {}
    dirnames = {}

    for file in request.files.getlist('pdfs[]'):
        filename = secure_filename(file.filename)
        dirname, extension = filename.rsplit('.', 1)
        dirname, dirnames = utils.gen_dirnames(dirname, dirnames)
        test_dir = os.path.join(testdir, dirname)
        os.makedirs(test_dir, exist_ok=True)
        file.save(os.path.join(test_dir, filename))
        utils.convert_to_img(test_dir, filename, dpi=dpi)
        if config['_1toN']:
            infos = special_extract_from_pdf(template_dir, test_dir, config)
        else:
            infos = extract_from_pdf(template_dir, test_dir, drawing)
        all_pdf_infos[filename] = infos

    save_result(upload_folder, all_pdf_infos, config['_1toN'])

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


def special_extract_from_pdf(template_dir, testdir, config):
    
    template_dir = os.path.join(template_dir, 'pages')
    test_dir = os.path.join(testdir, 'pages')
    template_img = utils.get_page(template_dir, config['_1toNonPage'])
    pages = len(os.listdir(test_dir))

    drawing_page = [x for x in config['drawing'] if x['page'] == config['_1toNonPage']]
    infos = {}

    for no_page in range(pages):
        start = time.time()
        test_img = utils.get_page(test_dir, no_page)
        img = alignement.align_to_template(test_img, template_img)
        info, img_show = extract.extract_text(img, drawing_page)
        extract.show_highlighted_img(testdir, no_page, img_show)
        info[f'extraction_time(sec)'] = round((time.time() - start), 2)
        infos[f'page#{no_page}'] = info
    
    return infos



@app.route('/file-choice')
def select_files():
   return render_template('file_choice.html') 


@app.route('/with-config/process', methods=['POST'])
def process_files():
    template = request.files.get('template')
    config = request.files.get('config')
    test_files = request.files.getlist('test')

    sess_id = utils.get_next_id(app.config['CONF_FOLDER'])
    
    upload_folder = os.path.join(app.config['CONF_FOLDER'], str(sess_id))
    template_dir = os.path.join(upload_folder, 'template_pdf')
    os.makedirs(template_dir)

    
    # save the drawing (config file)
    config.save(os.path.join(upload_folder, 'drawing.json'))
    with open(os.path.join(upload_folder, 'drawing.json'), 'r', encoding='utf-8') as json_file:
        config = json.load(json_file)
        dpi = config['dpi']
        config['drawing'] = utils.occurence_dict(config['drawing'])
        drawing = config['drawing']

    # save and convert to image the template pdf
    template.save(os.path.join(template_dir, secure_filename(template.filename)))
    utils.convert_to_img(template_dir, secure_filename(template.filename), dpi=dpi)
    
    
    # save all files in directory containing their name and convert them to images
    all_pdf_infos = {}
    dirnames = {}

    for file in test_files:
        filename = secure_filename(file.filename)
        dirname, extension = filename.rsplit('.', 1)
        dirname, dirnames = utils.gen_dirnames(dirname, dirnames)
        test_dir = os.path.join(upload_folder, 'test_pdf', dirname)
        os.makedirs(test_dir, exist_ok=True)
        file.save(os.path.join(test_dir, filename))
        utils.convert_to_img(test_dir, filename, dpi=dpi)
        if config['_1toN']:
            infos = special_extract_from_pdf(template_dir, test_dir, config)
        else:
            infos = extract_from_pdf(template_dir, test_dir, drawing)
        all_pdf_infos[filename] = infos

    save_result(upload_folder, all_pdf_infos, config['_1toN'])

    return {'sess_id': sess_id}




@app.route('/local/extract', methods=['GET', 'POST'])
def local_extract():

    tmp_dir = app.config['TEMP_FOLDER']
    
    template_dir = os.path.join(tmp_dir, 'template_pdf')
    test_dir = os.path.join(tmp_dir, 'test_pdf')
    os.makedirs(template_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)
    
    
    template = request.files.get('template')
    config = request.files.get('config')

    if request.method != 'POST' or not template or not config or not request.form.get('test'):
        return render_template('local_choice.html')

    config.save(os.path.join(tmp_dir, 'drawing.json'))
    with open(os.path.join(tmp_dir, 'drawing.json'), 'r', encoding='utf-8') as json_file:
        config = json.load(json_file)
        dpi = config['dpi']
        config['drawing'] = utils.occurence_dict(config['drawing'])
        drawing = config['drawing']

    template.save(os.path.join(template_dir, 'current.pdf'))
    utils.convert_to_img(template_dir, 'current.pdf', dpi=dpi)
    
    local_testdir = request.form.get('test')

    if not os.path.isdir(local_testdir):
        return Response('path entered does not exist or is not a directory', 400)


    all_pdf_infos = {}
    for file in os.listdir(local_testdir):
        
        name, *extension = file.rsplit('.', 1)
        old_filepath = os.path.join(local_testdir, file)
        new_filepath = os.path.join(test_dir, 'current.pdf')

        if not os.path.isfile(old_filepath) or len(extension) == 0 or extension[0] != 'pdf':
            continue

        if os.path.exists(os.path.join(test_dir, 'pages')):
            shutil.rmtree(os.path.join(test_dir, 'pages'))

        print('Processing', file)
        shutil.copyfile(old_filepath, new_filepath)
        utils.convert_to_img(test_dir, 'current.pdf', dpi=dpi)
        if config['_1toN']:
            infos = special_extract_from_pdf(template_dir, test_dir, config)
        else:
            infos = extract_from_pdf(template_dir, test_dir, drawing)
        all_pdf_infos[file] = infos
        
    save_result(tmp_dir, all_pdf_infos, config['_1toN'])

    return Response('OK', 200)


if __name__ == '__main__':
    app.run(debug=True) 