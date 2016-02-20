import sys

if sys.hexversion < 0x2060000:
    raise NotImplementedError('Python < 2.6 not supported.')

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup

with open('README.rst') as file:
    long_description = file.read()

setup(name='SettingsTree',
      version='0.3',
      description='Utilities to work with trees of settings.',
      long_description=long_description,
      author='Freja Nordsiek',
      author_email='fnordsie at gmail dt com',
      url='https://github.com/frejanordsiek/SettingsTree',
      packages=['SettingsTree'],
      license='LGPLv3+',
      keywords='settings',
      classifiers=[
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Development Status :: 3 - Alpha",
          "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
          "Operating System :: OS Independent",
          "Environment :: X11 Applications :: Qt",
          "Intended Audience :: Developers",
          "Topic :: Software Development",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Software Development :: User Interfaces",
          "Topic :: Software Development :: Widget Sets",
          ],
      test_suite='nose.collector',
      tests_require='nose>=1.0'
      )
