from setuptools import find_packages, setup

package_name = 'jaka_vision'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', [
            'launch/apriltag_detector.launch.py',
            'launch/gazebo_camera_bridge.launch.py',
        ]),
        ('share/' + package_name + '/urdf/inc', [
            'urdf/inc/jaka_camera_gazebo.xacro',
        ]),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='xiang',
    maintainer_email='1510311910@qq.com',
    description='JAKA ZU7 vision detection package for apriltag-based visual servoing',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'apriltag_detector_node = jaka_vision.apriltag_detector_node:main',
            'simulated_detector_node = jaka_vision.simulated_detector_node:main',
        ],
    },
)
