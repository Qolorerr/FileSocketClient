from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='filesocket',
    packages=['filesocket'] + ['filesocket.' + pkg for pkg in find_packages('filesocket')],
    version='0.1.2',
    description='Transferring data between PCs library',
    long_description=long_description,
    author='Mikhail Ivanov',
    author_email='qolorer@gmail.com',
    url='https://github.com/Qolorerr/FileSocketClient',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'requests>=2.28.1',
        'pyngrok>=5.2.1',
        'uvicorn>=0.20.0',
        'fastapi>=0.89.1',
        'starlette>=0.22.0',
        'python-multipart>=0.0.5'
    ],
)
