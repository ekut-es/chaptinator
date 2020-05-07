from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='chaptinator',
    version='0.6',
    packages=find_packages(),
    url="https://github.com/ekut-es/chaptinator",
    license='Unlicense',
    author="Michael Kuhn & Alexander von Bernuth",
    author_email="michael.kuhn@uni-tuebingen.de",
    description="Add chapters to video based on scene cuts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    entry_points = {
        'console_scripts': ['chaptinator=chaptinator.__main__:main'],
    }
)
