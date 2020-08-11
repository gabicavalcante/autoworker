from setuptools import setup, find_packages

INSTALL_REQUIRES = ["rq>=0.10.0", "osconf"]

setup(
    name="autoworker",
    version="0.8.0",
    packages=find_packages(exclude=["spec"]),
    url="https://github.com/gabicavalcante/autoworker",
    license="MIT",
    install_requires=INSTALL_REQUIRES,
    description="Start Python RQ Workers automatically",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7.4",
    ],
)
