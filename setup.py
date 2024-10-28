from setuptools import setup

from version import __version__

setup(
    name='genconfig',
    version=__version__,
    py_modules=['genconfig', 'version'],
    entry_points={
        'console_scripts': [
            'genconfig = genconfig:main'
        ]
    },
    install_requires=[
        'click',
        'PyYAML',
        'astor',
        'marshmallow',
    ]
)
