from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='libbtc1',
    version='0.2.2',
    packages=find_packages(),
    install_requires=requirements,
    author='Will Abramson',
    author_email='will@legreq.com',
    description='Experimental python implementation of the did:btc1 Method Specification',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    # url='https://github.com/yourusername/mypackage',
)