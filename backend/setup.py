from setuptools import setup, find_packages

with open("../README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="CoinCanvas",
    version="0.0.0",
    author="csc-510",
    author_email="sfang9@ncsu.edu",
    description="An expense tracking application with AI assistance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DFY-NCSU/CoinCanvas/blob/dev/README.md",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "CoinCanvas=app.main:start_application",
        ],
    },
)