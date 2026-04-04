from setuptools import setup

setup(
    name='hand_eye_calibration',
    version='0.1.0',
    packages=['hand_eye_calibration'],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/hand_eye_calibration']),
        ('share/hand_eye_calibration/launch', ['hand_eye_calibration/launch/calibrate.launch.py']),
        ('share/hand_eye_calibration/config', ['hand_eye_calibration/config/calibration_params.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@example.com',
    description='Eye-in-Hand hand-eye calibration using Apriltag',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'calibrator = hand_eye_calibration.calibrator:main',
        ],
    },
)
