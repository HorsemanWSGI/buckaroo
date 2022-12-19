from setuptools import setup


setup(
    name='buckaroo',
    install_requires = [
        'autoroutes',
    ],
    extras_require={
        'test': [
            'pytest',
            'pyhamcrest',
        ]
    }
)
