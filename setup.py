import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kamaeleon",
    version="0.0.2",
    author="Julian",
    author_email="julian@edyoucated.org",
    description="Check out readme.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "dash",
        "pandas"
    ]
)
