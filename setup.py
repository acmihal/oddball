from setuptools import setup, find_packages

setup(
    name='oddball',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=['z3'],
    entry_points={
        'console_scripts': [
            'oddball=oddball:main',
        ],
    },
)
