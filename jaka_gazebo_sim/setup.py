import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'jaka_gazebo_sim'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Include launch files
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        # Include world files
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.world')),
        # Include URDF files
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.xacro')),
        (os.path.join('share', package_name, 'urdf', 'inc'), glob('urdf/inc/*.xacro')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='xiang',
    maintainer_email='1510311910@qq.com',
    description='JAKA ZU7 Gazebo simulation with eye-in-hand camera',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        ],
    },
)
