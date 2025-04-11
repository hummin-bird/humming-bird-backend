from setuptools import setup, find_packages

setup(
    name="humming-bird-backend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-dotenv",
        "pydantic",
        "pydantic-settings",
        "python-multipart",
    ],
) 