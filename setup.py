from distutils.core import setup

setup(
    name = 'dukpt',
    version = '1.0.1',
    py_modules = ['dukpt'],
    long_description = open('README.md').read(),
    long_description_content_type="text/markdown",
    install_requires=["bitstring==3.1.5", "pycryptodome==3.14.1"],
    python_requires=">=3.2",
)