import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyaspic", # Replace with your own username
    version="0.0.1",
    author="Mark Snaith",
    author_email="mark@arg.tech",
    description="Package for creating and evaluating ASPIC+ argumentation systems and theories",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/argtech/py-aspic",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
