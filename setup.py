from setuptools import setup, find_packages

setup(
    name='adb_tool',
    version='0.0.1',
    author='Shota Iuchi',
    author_email='shotaiuchi.develop@gmail.com',
    description='adb_tool is a tool for Android Debug Bridge (adb).',
    url='https://github.com/ShotaIuchi/adb_tool',
    license='MIT',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'chardet',
    ],
    include_package_data=True
)
