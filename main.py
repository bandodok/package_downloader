import os
import random
import shutil
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


app = FastAPI()
app.mount('/static', StaticFiles(directory="static"), name="static")


ZIP_FOLDER = 'zip'
PACKAGE_FOLDER = 'pack'


class Data(BaseModel):
    platform: str
    python_version: str
    package: str


@app.get('/pip')
def get_pip_form():
    clear_temp_folders()
    with open('main_form.html', 'r') as html:
        html_content = html.read()
    return HTMLResponse(content=html_content, status_code=200)


@app.get('/package')
def download_package(key: str, name: str):
    f = f'{PACKAGE_FOLDER}\\{key}\\{name}'
    return FileResponse(f, filename=name)


@app.get('/archive')
def download_archive(key: str, name: str):
    tmpdir = f'{PACKAGE_FOLDER}\\{key}'
    arch = shutil.make_archive(f'{ZIP_FOLDER}\\{key}_{name}', 'zip', tmpdir)
    return FileResponse(arch, filename=f'{name}.zip')


@app.post('/pip')
async def handle_form(request: Request):
    body = await request.json()
    platform = body['platform']
    python_version = body['python_version']
    package = body['package']

    key = generate_key()
    tmpdir = f'{PACKAGE_FOLDER}\\{key}'
    os.mkdir(tmpdir)

    get_packages(tmpdir, platform, python_version, package)

    packages = get_packages_names(tmpdir)
    data = {
        'key': key,
        'target_package': package,
        'packages': packages
    }

    return JSONResponse(data)


def get_packages_names(folder) -> list[str]:
    return [f.name for f in os.scandir(folder)]


def get_packages(dest: str, platform: str, python_version: str, package: str):
    command = (
        'python -m pip download',
        f'--platform {platform}',
        f'--python-version {python_version}',
        f'-d "{dest}"',
        f'--only-binary=:all: {package}'
    )
    os.system(' '.join(command))


def generate_key():
    key = ''
    key_len = 10
    alphabet: str = 'abcdefghijklmnopqrstuvwxyz1234567890_'
    for _ in range(key_len):
        key += random.choice(alphabet)
    return key


def clear_temp_folders():
    now = datetime.now().timestamp()
    delay = 300  # 5 mins

    if not os.path.isdir(PACKAGE_FOLDER):
        os.mkdir(PACKAGE_FOLDER)
    if not os.path.isdir(ZIP_FOLDER):
        os.mkdir(ZIP_FOLDER)

    for f in os.scandir(PACKAGE_FOLDER):
        if now - f.stat().st_mtime > delay:
            shutil.rmtree(f)

    for f in os.scandir(ZIP_FOLDER):
        if now - f.stat().st_mtime > delay:
            os.remove(f)


def clear_zip_files():
    files = os.scandir()
    for f in files:
        if f.name.endswith('.zip'):
            os.remove(f.name)


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=5000, log_level='info')
