from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="octoprint-cli",
    packages=find_packages(),
    version="3.2.2",
    entry_points={
        "console_scripts": [
            "octoprint-cli=octoprint_cli.__main__:main"
        ]
    },
    author="Ivy Fan-Chiang",
    author_email="userblackbox@tutanota.com",
    description="Command line tool for controlling your OctoPrint 3D printer server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/UserBlackBox/octoprint-cli",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Environment :: Console"
    ],
    python_requires='>=3.6',
    install_requires=['requests>=2.23.0', 'termcolor>=1.1.0']
)