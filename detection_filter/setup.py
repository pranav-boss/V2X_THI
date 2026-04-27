from setuptools import find_packages, setup

package_name = 'detection_filter'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Roman',
    maintainer_email='user@todo.todo',
    description='ROS 2 node to filter out specific classes from Cooperative Perception detections',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'filter_node = detection_filter.filter_node:main'
        ],
    },
)
