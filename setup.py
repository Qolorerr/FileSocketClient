from setuptools import setup, find_packages

setup(
    name='qhelper_client',
    packages=['qhelper_client'] + ['qhelper_client.' + pkg for pkg in find_packages('qhelper_client')],
    install_requires=[
        'requests == "2.28.1"',
        'python_version == "3.9"',
        'pyngrok == "5.2.1"',
        'uvicorn=="0.20.0"',
        'fastapi=="0.89.1"',
        'starlette=="0.22.0"',
    ],
)
