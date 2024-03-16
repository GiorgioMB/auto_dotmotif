"""This module sets up the package for distribution."""
from setuptools import setup, find_packages
setup(
    name='automotifs',
    version='1.0.1',
    packages=find_packages(),
    description='A wrapper for automatic Motif Detection',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Giorgio Micaletto',
    author_email='giorgio.micaletto@studbocconi.it',
    url='https://github.com/GiorgioMB/auto_dotmotif/',
    install_requires=[
        'pandas>=1.1.5',
        'pylint>=2.6.0',
        'numpy>=1.23',
        'dotmotif>=0.14.0',
        'networkx>=3.2.1'
    ],
    python_requires='>=3.6',
)
