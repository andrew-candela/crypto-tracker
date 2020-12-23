import setuptools

setuptools.setup(
    # we don't intend to upload this to PyPi, so don't worry too much about
    # name, version etc
    name="crypto-notifier",
    version="0.0.1",
    description="Let us know about some crypto metrics!",
    packages=setuptools.find_packages(),
    python_requires='>=3.7'
)
