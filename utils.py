import fitz
import os


def convert_to_img(template_dir, filename):
    
    doc = fitz.open(os.path.join(template_dir, filename))
    nb_pages = doc.page_count
    for no_page in range(nb_pages):
        page = doc.load_page(no_page)
        px = page.get_pixmap(dpi=120)
        name = '.'.join(filename.split('.')[:-1])
        px.save(os.path.join(template_dir, f'{name}_p{no_page}.png'))
    doc.close()
    return nb_pages


def get_next_id(upload_folder):

    list_folder = [int(x) for x in os.listdir(upload_folder) if x.isnumeric()]
    if not list_folder:
        return 1
    return max(list_folder) + 1


def get_page(upload_folder, template_id, page):
    file_list = os.listdir(os.path.join(upload_folder, str(template_id)))
    pagename = [x for x in file_list if f'p{page}.png' in x]
    assert len(pagename) > 0, f'Page n°{page} doesn\'t exist in upload folder'
    return str(template_id) + '/' + pagename[0]