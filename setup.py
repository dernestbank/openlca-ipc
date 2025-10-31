from setuptools import setup, find_packages

setup(
    name="olca-utils",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "olca-ipc>=2.4.0",
        "olca-schema>=2.4.0", 
        "numpy>=1.24.0",
    ],
    extras_require={
        "full": [
            "matplotlib>=3.7.0",
            "pandas>=2.0.0",
            "scipy>=1.10.0",
        ]
    },
    python_requires=">=3.8",
    author="LCA Team",
    description="Professional utilities for openLCA IPC operations",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
)