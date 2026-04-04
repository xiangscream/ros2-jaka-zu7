from setuptools import setup

package_name = 'swap_fsm'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name + '/launch', ['swap_fsm/launch/swap_fsm.launch.py']),
        ('share/' + package_name + '/action', ['swap_fsm/action/Swap.action']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@example.com',
    description='Swap FSM package with 12-step battery swap process',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'swap_fsm_node = swap_fsm.swap_fsm_node:main',
        ],
    },
)
