import setuptools

# with open("README.md", "r") as fh:
#     long_description = fh.read()

setuptools.setup(
    # we don't intend to upload this to PyPi, so don't worry too much about
    # name, version etc
    name="crypto-notifier",
    version="0.0.1",
    description="Let us know about some crypto metrics!",
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    url="https://fill-this-in-later.com",
    packages=setuptools.find_packages(),
    python_requires='>=3.7'
)
