import os
import re
from codecs import open

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
print(here)
with open(os.path.join(here, "README.md"), encoding='utf-8') as f:
    long_description = f.read()
long_description_content_type = "text/markdown"

with open(os.path.join(here, "src", "dnslib", "__init__.py")) as f:
    match = re.search(r'VERSION = "(.+?)"', f.read())
    assert match
    VERSION = match.group(1)

setup(
    name='dnslib',
    version=VERSION,
    description='Simple library to encode/decode DNS wire-format packets',
    long_description=long_description,
    long_description_content_type=long_description_content_type,
    author='PaulC',
    url='https://github.com/paulc/dnslib',
    packages=find_packages(where="src"),
    package_data={'': ['LICENSE', 'README.md', 'CHANGELOG.md']},
    package_dir={'': 'src'},
    python_requires='>=3.6.0',
    include_package_data=True,
    license='BSD',
    classifiers = [
        "License :: OSI Approved :: BSD",
        "Development Status :: 5 - Production/Stable",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Internet :: Name Service (DNS)",
        "Topic :: System :: Networking",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
