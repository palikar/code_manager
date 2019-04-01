#!/usr/bin/python

from distutils.core import setup  # pylint: disable=E0611, E0401

import sys
import setuptools

from code_manager.version import __version__

if sys.version_info < (3, 3):
    print("THIS MODULE REQUIRES PYTHON 3.3+. YOU ARE CURRENTLY\
    USING PYTHON {0}".format(sys.version))
    sys.exit(1)

setup(
    name="CodeManager",
    version=__version__,
    package_data={'code_manager': ['data/*', 'install_scripts/*']},
    include_package_data=True,
    author="Stanislav Arnaudov",
    author_email="stanislav_ts@abv.bg",
    description="Utility for automatic downloading, compiling and \
 installing softaware from internet.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    license="GNU General Public License v3.0",
    keywords="package code manager utility installation downloading compiling",
    url="https://github.com/palikar/code_manager",
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    entry_points={
        'console_scripts': [
            'code-manager = code_manager.main:main'
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Archiving :: Mirroring",
        "Topic :: System :: Archiving :: Packaging",
        "Topic :: System :: Installation/Setup"
    ],
)
