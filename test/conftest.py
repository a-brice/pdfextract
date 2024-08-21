import pytest 
import pathlib
import os 
import shutil
import time


@pytest.fixture
def basedir():
    return pathlib.Path(__file__).parent.resolve()


@pytest.fixture
def remove_testdir():
    pagedir1 = pathlib.Path(__file__).parent.resolve() / 'img' / 'pages'
    pagedir2 = pathlib.Path(__file__).parent.resolve() / 'data' / 'pages'


    if os.path.exists(pagedir1):
        shutil.rmtree(pagedir1, ignore_errors=True)
        time.sleep(0.5)

    if os.path.exists(pagedir2):
        shutil.rmtree(pagedir2, ignore_errors=True)
        time.sleep(0.5)
    
    yield

    if os.path.exists(pagedir1):
        shutil.rmtree(pagedir1, ignore_errors=True)
        time.sleep(0.5)

    if os.path.exists(pagedir2):
        shutil.rmtree(pagedir2, ignore_errors=True)
        time.sleep(0.5)