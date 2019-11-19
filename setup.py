from setuptools import setup





setup(
    name="instagraph",
    version="0.1",
    description="Instagram social network exploration tools",
    classifiers=[
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="decorator delegation ABC",
    url="http://github.com/monomonedula/abc-delegation",
    author="Vladyslav Halchenko",
    author_email="valh@tuta.io",
    license="Apache License Version 2.0",
    packages=["instagraph"],
    test_suite="nose.collector",
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    install_requires=["psycopg2"]
)
