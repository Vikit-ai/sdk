from setuptools import setup

setup(
    name="vikit.ai",
    version="0.1.0",
    description="AI Video Generation Software Development Kit",
    url="https://github.com/leclem/aivideo",
    author="Jeffmac",
    author_email="JFmac@vikit.ai",
    packages=[
        "src",
        "vikit.common",
        "vikit.gateways",
        "vikit.prompt",
        "vikit.video",
        "vikit.wrappers",
    ],
    install_requires=[
        "replicate==0.24.0",
        "pysrt==1.1.2",
        "ffmpeg-python==0.2.0",
        "sib_api_v3_sdk==7.6.0",
        "numpy==1.26.4",
        "google-cloud-storage==2.14.0",
        "loguru==0.7.2",
        "retry-requests==2.0.0",
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
)
