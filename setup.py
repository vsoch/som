from setuptools import setup, find_packages
import sys
import os

requirements = ['requests']

setup(
    name='som',
    version='0.0.1',
    license='MIT',
    description='python tools for school of medicine',
    author="Vanessa Sochat",
    author_email='vsochat@stanford.edu',
    url='https://github.com/radinformatics/somtools',
    packages=find_packages(), 
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: System :: Shells',
        'Topic :: Terminals',
        'Topic :: Utilities'
    ],
)
