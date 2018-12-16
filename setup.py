import os
from setuptools import setup, find_packages
from wheel.bdist_wheel import bdist_wheel
from wheel.pep425tags import get_platform

class PlatformBDistWheel(bdist_wheel):
    def initialize_options(self):
        super(PlatformBDistWheel, self).initialize_options()
        if self.plat_name is None:
            self.plat_name = get_platform()

setup(
    name=os.environ['TOOL_NAME'],
    version=os.environ['TOOL_VERSION'],
    include_package_data=True,
    data_files=[
        ('bin', [os.environ['TOOL_NAME']])
    ],
    cmdclass={
        'bdist_wheel': PlatformBDistWheel
    }
)
