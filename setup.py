from setuptools import setup, find_packages

setup(
    name='qhelper_client',
    packages=['qhelper_client'] + ['qhelper_client.' + pkg for pkg in find_packages('qhelper_client')],
    install_requires=[
        'requests == "2.28.1"',
        'websocket-client == "1.3.3"',
        'rel @ git+https://github.com/bubbleboy14/registeredeventlistener.git',
        'python_version == "3.9"',
    ],
)
