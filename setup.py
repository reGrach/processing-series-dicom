from setuptools import setup, find_packages
import __init__

with open("README", 'r') as f:
    long_description = f.read()

setup(
    name='ProcessingSeriesDICOM',
    version=__init__.__version__,
    packages=find_packages(),
    url='',
    license='',
    author='reGrach',
    author_email='germangrach.94@ya.ru',
    description='The package is intended for processing a series of images DICOM CT',
    install_requires=['pydicom', 'numpy', 'scipy', 'scikit-image', 'matplotlib']
)
