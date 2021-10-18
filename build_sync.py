from setuptools import find_packages, setup
from unasync import cmdclass_build_py

setup(
    packages=find_packages(),
    cmdclass={"build_py": cmdclass_build_py()},  # type: ignore
)
