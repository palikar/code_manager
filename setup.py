#!/usr/bin/env python3

import sys, os
import setuptools

import code_manager

if sys.version_info < (3, 3):
    print("THIS MODULE REQUIRES PYTHON 3.3+. YOU ARE CURRENTLY USING PYTHON {0}".format(sys.version))
    sys.exit(1)


exec(open('code_manager/version.py').read())

setuptools.setup(
    name="CodeManager",
    version=__version__,
    package_data={
            'ranger': [
                'data/*',
                'config/rc.conf',
                'config/rifle.conf',
            ],
        },
    include_package_data=True,
    author="Stanislav Arnaudov",
    author_email="stanislav_ts@abv.bg",
    description="Utility for automatic downloading, compiling and installing softaware from internet.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    license="GNU General Public License v3.0",
    keywords="code manager utility installation downloading compiling",
    url="https://github.com/palikar/code_manager",
    entry_points={
        'console_scripts': [
            'code-manager = code_manager.code_manager:main'
        ]
    },
    # data_files=[('config', ['packages.json', 'cache', 'conf'])],
    classifiers=[
        "Development Status :: 1 - Proof of concept",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: GNU General Public License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Linux :: Debian",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Code Management",
    ],
)
