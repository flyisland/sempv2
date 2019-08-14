from setuptools import setup

setup(name='sempv2',
      version='0.1',
      description='Backing Up and Restoring Solace PubSub+ VPN Configs with SEMPv2',
      url='http://github.com/flyisland/sempv2',
      author='Island Chen',
      author_email='island.chen@outlook.com',
      license='MIT',
      packages=['sempv2'],
      install_requires=[
          'click',
          'importlib_resources'
      ],
      entry_points='''
            [console_scripts]
            sempv2=sempv2.cmd:cli
      ''',
      zip_safe=False)
