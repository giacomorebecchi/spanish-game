from setuptools import find_packages, setup

setup(
    name="spanish-game",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    version="0.0.1",
    description="""
    Game to exercise with the spanish vocabulary, designed for Italian motherthongues.
    """,
    author="Giacomo Rebecchi",
    license="",
)
