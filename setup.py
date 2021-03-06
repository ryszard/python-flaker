from setuptools import setup, find_packages
import sys

install_requires = ['poster']
if sys.version < 2.6:
    install_requires.append('simplejson')

setup(
    name = "flaker",
    version = "0.2.5",
    description="Flaker.pl client",
    author="Ryszard Szopa",
    author_email="ryszard.szopa@gmail.com",
    url="http://github.com/ryszard/python-flaker/",
    packages = find_packages(),
    keywords='internet flaker api',
    zip_safe=True,
    long_description = """\
Client library for flaker.pl's API. See http://flaker.pl and http://blog.flaker.pl/api/ for more information.""",
    install_requires = install_requires,
    license = 'MIT',
    package_data = {
        '': ['*.txt', '*.rst', '*.markdown'],},
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Internet",
      ],


)
