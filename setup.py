from setuptools import setup, find_packages

setup(name='sempv2',
      version='0.1.1',
      description='Backing Up and Restoring Solace PubSub+ Configs with SEMPv2',
      url='http://github.com/flyisland/sempv2',
      author='Island Chen',
      author_email='island.chen@outlook.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'click',
          'jinja2'
      ],
      entry_points={
        "console_scripts": [
            "sempv2=sempv2.cmd:cli",
        ]
      },
      include_package_data=True,
      package_data={
            '': ['*.json'],
      },
      zip_safe=False)
