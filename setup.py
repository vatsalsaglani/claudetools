from setuptools import setup, find_packages

setup(
    name="claudetools",
    version="0.6.0",
    author="Vatsal J. Saglani",
    author_email="saglanivatsal@gmail.com",
    description=
    "Claudetools is a Python library that enables function calling with the Claude 3 family of language models from Anthropic.",
    long_description=open("Readme.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/vatsalsaglani/claudetools",
    packages=find_packages(),
    install_requires=["httpx==0.25.0", "anthropic==0.19.1", "pydantic==2.4.2"],
    python_requires=">=3.7")
