from setuptools import setup, find_packages

setup(
    name='filesocket',
    packages=['filesocket'] + ['filesocket.' + pkg for pkg in find_packages('filesocket')],
    version='0.1.0',
    description='Transferring data between PCs library',
    author='Qolorer',
    license='MIT',
    install_requires=[
        'requests == "2.28.1"',
        'python_version == "3.9"',
        'pyngrok == "5.2.1"',
        'uvicorn=="0.20.0"',
        'fastapi=="0.89.1"',
        'starlette=="0.22.0"',
    ],
)
