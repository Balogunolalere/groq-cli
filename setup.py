from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="groq-cli",
    version="0.1.0",
    author="Balogunolalere",
    author_email="lordareello@gmail.com",
    description="A CLI tool for generating and executing Linux commands using Groq API",
    long_description_content_type="text/markdown",
    url="https://github.com/Balogunolalere/groq-cli",
    packages=find_packages(),
    install_requires=[
        "groq",
        "python-dotenv",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "groq-cli=groq_cli:main",
        ],
    },
)