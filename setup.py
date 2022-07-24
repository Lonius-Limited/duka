from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in duka/__init__.py
from duka import __version__ as version

setup(
	name="duka",
	version=version,
	description="Procurement, Warehousing, Transport and Manufacturing for B2Bs",
	author="Lonius Devs",
	author_email="info@lonius.co.ke",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
