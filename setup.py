from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='libbtc1',
    version='0.1',
    packages=find_packages(),
    install_requires=requirements,
    author='Will Abramson',
    author_email='will@legreq.com',
    description='A short description of your package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    # url='https://github.com/yourusername/mypackage',
)