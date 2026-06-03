from setuptools import find_packages, setup

package_name = 'vision_project'

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
    maintainer='agamy',
    maintainer_email='agamy@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        'camera_node = vision_project.camera_node:main',
        'vision_node = vision_project.vision_node:main',
        'test_camera = vision_project.test_camera:main',
        ],
    },
)
