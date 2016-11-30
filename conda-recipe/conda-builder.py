import json
import os
import shutil
import tempfile

from jinja2 import Environment

PROJECT_ROOT = os.path.realpath(os.path.join(
    os.path.dirname(__file__),
    '..'
))
LIB_NAME = 'measurement_stats'

settings_path = os.path.join(PROJECT_ROOT, LIB_NAME, 'settings.json')
with open(settings_path, 'r+') as f:
    settings = json.load(f)

temp_directory = tempfile.mkdtemp(prefix='{}-build-'.format(LIB_NAME))

shutil.copytree(
    os.path.join(PROJECT_ROOT, LIB_NAME),
    os.path.join(temp_directory, LIB_NAME)
)

shutil.copytree(
    os.path.join(PROJECT_ROOT, 'conda-recipe'),
    os.path.join(temp_directory, 'conda-recipe')
)

for item in os.listdir(PROJECT_ROOT):
    item_path = os.path.join(PROJECT_ROOT, item)
    if os.path.isfile(item_path):
        shutil.copy2(item_path, os.path.join(temp_directory, item))

meta_path = os.path.join(PROJECT_ROOT, 'conda-recipe', 'meta.yaml.template')
with open(meta_path, 'r+') as f:
    meta_template = f.read()

meta_target_path = os.path.join(temp_directory, 'conda-recipe', 'meta.yaml')
with open(meta_target_path, 'w+') as f:
    f.write(
        Environment()
        .from_string(meta_template)
        .render(dict(
            VERSION=settings['version'],
            PATH=temp_directory
        ))
    )

print('[PURGE]: Remove accumulated conda builds')
os.system('conda build purge')

print('[BUILD]: Assembling the conda package')
os.system('conda build {}'.format(
    os.path.join(temp_directory, 'conda-recipe')
))

print('[DONE]: Package built')

shutil.rmtree(temp_directory)
