"""This module sets up the package for distribution."""
from setuptools import setup, find_packages
with open('requirements.txt') as f:
    requirements = f.read().splitlines()
setup(
    name='automotifs',
    version='0.6',
    packages=find_packages(),
    description='A wrapper for automatic Motif Detection',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Giorgio Micaletto',
    author_email='giorgio.micaletto@studbocconi.it',
    url='https://github.com/GiorgioMB/auto_dotmotif/',
    install_requires=requirements,
    python_requires='>=3.6',
)
