#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from setuptools import find_packages, setup

setup(
    name="Vikit-SDK",
    version="0.2.2",
    author="Vikit.ai Team",
    author_email="christian@vikit.ai, jf@vikit.ai",
    description="Video generator SDK by orchestrating and tuning generative AI",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Vikit-ai/sdk",
    packages=find_packages(),
    python_requires=">=3.10",
)
