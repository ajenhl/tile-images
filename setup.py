#!/usr/bin/env python3

from setuptools import setup


with open('README.rst') as fh:
    long_description = fh.read()

setup(
    name='tile-images',
    version='1.0',
    description='Script to generate PDFs from images, tiled and double-sided',
    long_description=long_description,
    author='Jamie Norrish',
    author_email='jamie@artefact.org.nz',
    url='https://github.com/ajenhl/tile-images',
    python_requires='~=3.6',
    license='GPLv3+',
    packages=['tiler'],
    entry_points={
        'console_scripts': [
            'tile-images=tiler.__main__:main',
        ],
    },
    install_requires=['img2pdf', 'Pillow'],
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Topic :: Multimedia :: Graphics :: Presentation',
    ],
)
