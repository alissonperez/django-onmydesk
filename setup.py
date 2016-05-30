import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-onmydesk',
    version='0.1',
    packages=find_packages(exclude=('tests*',)),
    include_package_data=True,
    license='BSD License',
    description='A simple Django app to build reports.',
    long_description=README,
    url='https://github.com/knowledge/knowledge4life/',
    author='Alisson R. Perez',
    author_email='alisson.perez@knowledge4.life',
    install_requires=[
        'XlsxWriter==0.8.3',  # Used by XLSXOutput
        'filelock==2.0.6',
        'awesome-slugify==1.6.5',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
