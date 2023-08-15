"""Installer for the kitconcept.solr package."""
from pathlib import Path
from setuptools import find_packages
from setuptools import setup


long_description = f"""
{Path("README.md").read_text()}\n
{Path("CHANGES.md").read_text()}\n
"""


setup(
    name="kitconcept.solr",
    version="1.0.0a3",
    description="An opinionated Solr integration for Plone",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 6.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone Solr",
    author="kitconcept GmbH",
    author_email="info@kitconcept.com",
    url="https://github.com/kitconcept/kitconcept.solr",
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["kitconcept"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    project_urls={
        "PyPI": "https://pypi.python.org/pypi/kitconcept.solr",
        "Source": "https://github.com/kitconcept/kitconcept.solr",
        "Tracker": "https://github.com/kitconcept/kitconcept.portal/issues",
    },
    install_requires=[
        "Plone>=6.0.0",
        "plone.restapi>=8.40.0",
        "plone.api",
        "setuptools",
        "collective.solr>=9.0.1",
    ],
    extras_require={
        "test": [
            "zest.releaser[recommended]",
            "zestreleaser.towncrier",
            "plone.app.testing",
            "plone.restapi[test]",
            "pytest",
            "pytest-cov",
            "pytest-docker",
            "pytest-plone>=0.2.0",
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = kitconcept.solr.locales.update:update_locale
    """,
)
