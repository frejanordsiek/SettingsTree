import ez_setup
ez_setup.use_setuptools()

from setuptools import setup

with open('README.rst') as file:
    long_description = file.read()

setup(name='SettingsTree',
      version='0.2',
      description='Utilities to work with trees of settings.',
      long_description=long_description,
      author='Freja Nordsiek',
      author_email='fnordsie at gmail dt com',
      url='https://github.com/frejanordsiek/SettingsTree',
      packages=['SettingsTree'],
      license='BSD',
      keywords='settings',
      classifiers=[
          "Programming Language :: Python :: 3",
          "Development Status :: 3 - Alpha",
          "License :: OSI Approved :: BSD License",
          "Operating System :: OS Independent",
          "Environment :: X11 Applications :: Qt",
          "Intended Audience :: Developers",
          "Topic :: Software Development",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Software Development :: User Interfaces",
          "Topic :: Software Development :: Widget Sets",
          ],
      )
