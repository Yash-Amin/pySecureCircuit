from setuptools import setup, find_packages


with open("README.md") as f:
    LONG_DESCRIPTION = f.read()

with open("requirements.txt") as f:
    INSTALL_LIBRARIES = f.read().splitlines()


setup(
    name="pysecurecircuit",
    version="0.0.3",
    author="Yash Amin",
    author_email="yamin@hawk.iit.edu",
    description="Python library for secure multi-party computation using garbled circuits",
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=INSTALL_LIBRARIES,
    keywords=[
        "python",
        "mpc",
        "secure mpc",
        "garbled circuit",
        "multi party computation",
    ],
    project_urls={
        "Source Code": "https://github.com/Yash-Amin/pySecureCircuit",
    },
    classifiers=[],
)
