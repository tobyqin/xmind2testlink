"""
Use this script to upload a pypi package, require below package:

    pip install setuptools -U
    pip install wheel -U
    pip install twine -U


This is the script to release manually, now the package can be released via Github Actions:
- https://github.com/tobyqin/xmind2testlink/actions

"""
import os

egg = 'dist'

if os.path.exists(egg):
    for f in os.listdir(egg):
        os.remove(os.path.join(egg, f))

os.system('python setup.py sdist bdist_wheel')
os.system('twine upload dist/*')
