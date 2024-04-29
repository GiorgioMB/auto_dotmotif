import os
from setuptools import setup, find_packages
from setuptools.command.install import install

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        # Running pip install for nx-cugraph with the specified extra index URL
        os.system("pip install nx-cugraph-cu11 --extra-index-url https://pypi.nvidia.com")

setup(
    name='automotifs',
    version='1.5', 
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
        'networkx>=3.2.1',
        'matplotlib>=3.8.0',
        'seaborn>=0.12.2'
    ],
    python_requires='>=3.6',
    cmdclass={
        'install': PostInstallCommand,
    }
)
