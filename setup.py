import setuptools

setuptools.setup(
    name="prestic",
    version="0.0.2",
    license="MIT",
    author="Alex Duchesne",
    author_email="alex@alexou.net",
    description="Prestic is a profile manager and task scheduler for restic",
    url="https://github.com/ducalex/prestic",
    packages=["prestic"],
    package_data={
        "prestic": ["icon.png", "icon-run.png"],
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pystray",
        "keyring"
    ],
    entry_points={
        "console_scripts": [
            "prestic=prestic:main",
        ],
        "gui_scripts": [
            "prestic-gui=prestic:gui",
        ],
    },
)
