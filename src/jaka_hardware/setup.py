from setuptools import setup

setup(
    name='jaka_hardware',
    version='0.1.0',
    packages=['jaka_hardware'],
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/jaka_hardware']),
        ('share/jaka_hardware', ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='User',
    maintainer_email='user@example.com',
    description='JAKA ZU7 hardware bridge for MoveIt2',
    license='MIT',
    entry_points={
        'console_scripts': [
            'jaka_bridge_node = jaka_hardware.jaka_bridge_node:main',
        ],
    },
)
