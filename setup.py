import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tutake",
    version="0.0.1",
    author="rmfish",
    author_email="rmfish.io@gmail.com",
    description="Take quant data from web to local.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rmfish/tutake",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)