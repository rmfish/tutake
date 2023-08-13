import setuptools

# from pip.req import parse_requirements

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name="tutake",
    version="0.0.4",
    author="rmfish",
    author_email="rmfish.io@gmail.com",
    description="Take quant data from web to local.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rmfish/tutake",
    install_requires=[
        "pandas==1.5.1",
        "pendulum==2.1.2",
        "PyYAML==6.0",
        "requests==2.28.1",
        "SQLAlchemy==1.4.42",
        "tushare==1.2.85",
        "apscheduler~=3.9.1.post1"
    ],
    extras_require={"tutake.cg": ["yapf==0.32.0", "Jinja2==3.1.2"]},
    packages=setuptools.find_packages(exclude=("test",)),
    package_data={'tutake.utils': ['*']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
