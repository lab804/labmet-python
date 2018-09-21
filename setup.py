import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'labmet'))
from version import VERSION

install_requires = [
    'pandas >= 0.23.4',
    'numpy >= 1.15.1',
    'requests >= 2.19.1',
    'inflection >= 0.3.1',
    'six',
]

packages = [
    'labmet'
]

setup(
    name='Labmet',
    description='Package for labmet API access',
    keywords=['labmet', 'API', 'data', 'weather', 'bigdata'],
    long_description="",
    version=VERSION,
    author='LabMet',
    author_email='contato@labmet.com.br',
    maintainer='LabMet Development Team',
    maintainer_email='contato@labmet.com.br',
    url='https://github.com/lab804/labmet-python',
    license='BSD',
    install_requires=install_requires,
    packages=packages
)
