from setuptools import setup, find_packages

with open('.\\requirements.txt', encoding='utf-16') as f:
    required = f.read().splitlines()

setup(
    name='astHint',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[required],
    entry_points='''
        [console_scripts]
        astHint=astHint:ast_hint
    '''

)
