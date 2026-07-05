from setuptools import setup, find_packages

setup(
    name="covid_data_analysis",
    version="0.1.0",
    description="COVID-19 Data Analysis Pipeline",
    author="Data Engineering Team",
    packages=find_packages(include=["src", "src.*"]),
    install_requires=[
        "pyspark>=3.4.0",
        "pandas>=2.0.0",
        "minio>=7.2.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.9",
)
