"""
Setup script for Psi-freq Scalper
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="psi-freq-scalper",
    version="1.0.0",
    author="Psi-freq Development Team",
    description="Advanced algorithmic trading bot with Psi-frequency analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/somat3k/psychic-doodle-algit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "psi-freq-scalper=main:main",
        ],
    },
)
