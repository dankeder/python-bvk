import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as fh:
    install_requires = [line for line in fh if line and line[0] not in "#-"]

setuptools.setup(
    name="python-bvk",
    version="0.1.3",
    author="Dan Keder",
    author_email="dan.keder@protonmail.com",
    description="Python library for tracking water consumption from BVK (Brnenske vodarny a kanalizace, bvk.cz)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dankeder/python-bvk",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
