from setuptools import setup, find_packages

setup(
    name="openlca-ipc",
    version="0.1.0",
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
    python_requires=">=3.10",
    author="Ernest Boakye Danquah",
    author_email="dernestbanksch@gmail.com",
    description="A Python library for interacting with openLCA desktop application through the IPC protocol for life cycle assessment (LCA) workflows.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/dernestbank/openlca-ipc",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    keywords="openlca lca life-cycle-assessment ipc environmental-impact iso-14040 iso-14044",
)