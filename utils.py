import fitz
import numpy as np
import os
from PIL import Image


def convert_to_img(template_dir, filename):

    img_path = os.path.join(template_dir, 'pages')
    if not os.path.exists(img_path):
        os.mkdir(img_path)

    # for images file (png, jpg)
    if filename.rsplit('.', 1)[1] != 'pdf':
        img = Image.open(os.path.join(template_dir, filename))
        img.save(os.path.join(img_path, f'{filename.rsplit(".", 1)[0]}_$p#0.png'))
        return 1 # nb_pages = 1 since it's an image
    
    # for pdf file
    doc = fitz.open(os.path.join(template_dir, filename))
    nb_pages = doc.page_count
    for no_page in range(nb_pages):
        page = doc.load_page(no_page)
        px = page.get_pixmap(dpi=120)
        name = filename.rsplit('.', 1)[0]
        px.save(os.path.join(img_path, f'{name}_$p#{no_page}.png'))
    doc.close()

    return nb_pages


def get_next_id(upload_folder):

    list_folder = [int(x) for x in os.listdir(upload_folder) if x.isnumeric()]
    if not list_folder:
        return 1
    return max(list_folder) + 1


def get_page(directory, page, complete_path=True):
    file_list = os.listdir(directory)
    pagename = [x for x in file_list if f'_$p#{page}.png' in x]

    return os.path.join(directory, pagename[0]) if complete_path else pagename[0]




def occurence_dict(dic):
    
    keys = np.array([x['label'] for x in dic])
    keys, counts = np.unique(keys, return_counts=True)
    idx = np.where(counts > 1)[0]
    dupl_keys = dict(zip(keys[idx], np.zeros(idx.shape, np.int32)))
    for x in dic:
        if x['label'] in dupl_keys.keys():
            dupl_keys[x["label"]] += 1
            x['label'] = x['label'] + f'_{dupl_keys[x["label"]]}'
            
    return dic

def gen_dirnames(dirname:str, dirnames: dict):
    """Ensure there is no directory with the same names if there have multiple files with the same name"""
    if dirname in dirnames:
        dirnames[dirname] += 1
        return dirname + f'_{dirnames[dirname]}', dirnames
    else:
        dirnames[dirname] = 0
        return dirname, dirnames