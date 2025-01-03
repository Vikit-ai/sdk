from setuptools import setup, find_packages
import os


def read_version():
    version_file = os.path.join(os.path.dirname(__file__), "vikit", "version.py")
    with open(version_file, "r") as f:
        exec(f.read())
        return locals()["__version__"]


setup(
    name="vikit-ai-sdk-dev",
    version=read_version(),
    description="Vikit.ai Software Development Kit",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Vikit.ai",
    author_email="hello@vikit.ai",
    url="https://github.com/vikit-ai/sdk",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "aiohttp>=3.8.0",
        "aiofiles>=0.8.0",
        "google-cloud-storage>=2.0.0",
        "tenacity>=8.0.0",
        "pytest>=7.0.0",
        "pytest-asyncio>=0.18.0",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-asyncio",
            "pytest-cov",
            "black",
            "isort",
            "flake8",
            "wheel",
        ],
    },
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",  # Corrected classifier
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
