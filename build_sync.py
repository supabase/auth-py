from setuptools import find_packages, setup
from unasync import cmdclass_build_py

setup(
    packages=find_packages(exclude=["tests"]),
    # package_dir={"": "gotrue"},
    cmdclass={"build_py": cmdclass_build_py()},  # type: ignore
)
