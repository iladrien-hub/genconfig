import genconfig
from setuptools import setup

setup(
    name='genconfig',
    version=genconfig.__version__,
    py_modules=['genconfig'],
    entry_points={
        'console_scripts': [
            'genconfig = genconfig:main'
        ]
    },
    install_requires=['click', 'PyYAML']
)
