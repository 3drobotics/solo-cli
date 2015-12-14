from setuptools import setup, Extension
import platform

version = '1.1.1'

setup(name='solo-cli',
      zip_safe=True,
      version=version,
      description="Command line utility for Solo development.",
      long_description="Command line utility for Solo development.",
      url='https://github.com/3drobotics/solo-utils',
      author='3D Robotics',
      install_requires=[
          'docopt >= 0.6.2',
          'paramiko >= 1.15.2',
          'scp >= 0.10.0',
          'requests>=2.5.0',
          'pyopenssl',
          'ndg-httpsclient',
          'pyasn1',
      ],
      author_email='tim@3drobotics.com',
      classifiers=['Development Status :: 4 - Beta', 'Environment :: Console',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: Apache Software License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Scientific/Engineering'],
      entry_points={
          'console_scripts': [
              'solo = soloutils.__main__'
          ]
      },
      license='apache',
      packages=['soloutils'])
