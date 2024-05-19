from setuptools import setup, find_packages

setup(
    name="splint",
    version="0.1.0",
    packages=find_packages(where="src", include=["splint.*"]),
    # look in 'src' and include packages in 'splint' and its sub-packages
    package_dir={"": "src"},
)