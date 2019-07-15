from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='example',
      version='0.1',
      description='The example joke in the world',
      long_description=readme(),
#      # see https://pypi.python.org/pypi?%3Aaction=list_classifiers 
#      classifiers=[
#        'Development Status :: 3 - Alpha',
#        'License :: OSI Approved :: MIT License',
#        'Programming Language :: Python :: 3.4',
#        'Topic :: Text Processing :: Linguistic',
#      ],
#      keywords='example joke comedy flying circus',
#      url='http://github.com/storborg/example',
      author='fellowtech GmbH',
      author_email='support@fellowtech.de',
      license='MIT',
      packages=['example'],
#      install_requires=[
#          'markdown',
#      ],
      include_package_data=True,
      zip_safe=False,
)
