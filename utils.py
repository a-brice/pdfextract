import fitz
import os


def convert_to_img(template_dir, filename):
    
    doc = fitz.open(os.path.join(template_dir, filename))
    img_path = os.path.join(template_dir, 'pages')
    if not os.path.exists(img_path):
        os.mkdir(img_path)
    
    nb_pages = doc.page_count
    for no_page in range(nb_pages):
        page = doc.load_page(no_page)
        px = page.get_pixmap(dpi=120)
        name = '.'.join(filename.split('.')[:-1])
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

