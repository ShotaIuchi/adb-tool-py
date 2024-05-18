from setuptools import setup, find_packages

setup(
    name='adb-tool-py',
    version='0.1.0',
    author='Shota Iuchi',
    author_email='shotaiuchi.develop@gmail.com',
    description='adb-tool-py is a tool for Android Debug Bridge (adb).',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ShotaIuchi/adb-tool-py',
    license='MIT',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
    install_requires=[
        'chardet',
        'opencv-python',
    ],
    include_package_data=True
)
