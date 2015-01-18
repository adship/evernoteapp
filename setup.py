from mininote.constants import MININOTE_VERSION
from setuptools import setup, find_packages


with open('requirements.txt') as fh:
    install_requires = map(str.strip, fh.readlines())

setup(
    name = 'mininote',
    version = MININOTE_VERSION,
    author = 'mininote',
    author_email = 'mininoteapp@gmail.com',
    install_requires = install_requires,
    packages = ['mininote'],
    entry_points = {
        'console_scripts': [
            'mn = mininote.mn:main'
        ]}
)
