import glob
import setuptools
from typing import List

import gotrue


def get_scripts_from_bin() -> List[str]:
    """Get all local scripts from bin so they are included in the package."""
    return glob.glob("bin/*")


def get_package_description() -> str:
    """Returns a description of this package from the markdown files."""
    with open("README.md", "r") as stream:
        readme: str = stream.read()
    return readme


setuptools.setup(
    name="gotrue",
    version=gotrue.__version__,
    author="Joel Lee",
    author_email="joel@joellee.org",
    description="Python Client Library for GoTrue",
    long_description=get_package_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/supabase/gotrue-py",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    scripts=get_scripts_from_bin(),
    python_requires=">=3.7",
)
