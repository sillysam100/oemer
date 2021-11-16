import setuptools


with open("README.md") as red:
    ldest = red.read()

setuptools.setup(
    name='oemer',
    version='0.1.0-rc6',
    author='BreezeWhite',
    author_email='miyasihta2010@tuta.io',
    description='End-to-end Optical Music Recognition (OMR) system.',
    long_description=ldest,
    long_description_content_type='text/markdown',
    license_files=('LICENSE',),
    url='https://github.com/BreezeWhite/oemer',
    packages=setuptools.find_packages(),
    package_data={
    '': [
            'sklearn_models/*.model',
            'checkpoints/unet_big/metadata.pkl',
            'checkpoints/unet_big/arch.json',
            'checkpoints/seg_net/metadata.pkl',
            'checkpoints/seg_net/arch.json',
        ]
    },
    install_requires=[
        'onnxruntime-gpu',
        'opencv-python==4.5.3.56',
        'matplotlib',
        'pillow',
        'numpy==1.21.2',
        'scipy==1.6.2',
        'scikit-learn==0.24.2'
    ],
    extras_require={
        'full': ['tensorflow-gpu', 'tf2onnx']
    },
    entry_points={'console_scripts': ['oemer = oemer.ete:main']}
)
