import setuptools

setuptools.setup(name='autonomous', version='1.1',
    description='The autonomous libraries',
    author='Reza',
    #packages=setuptools.find_packages(),
    packages=['gps','libs'],
    #package_dir={'gps':'gps/', 'libs':'libs/', '.': '.'},
    package_data={'gps':['_gps.so']})

