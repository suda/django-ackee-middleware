import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-ackee-middleware",
    version="0.1.0",
    author="Wojtek Siudzinski",
    author_email="admin@suda.pl",
    description="Django middleware reporting requests to Ackee",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/suda/django-ackee-middleware",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
