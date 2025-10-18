from setuptools import setup, find_packages

setup(
    name="aivia",
    version="0.1.0",
    description="AIVIA - Natural Language to Neo4j Cypher Query Engine",
    author="SUNNYZHENG",
    author_email="your-email@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "neo4j>=5.0.0",
        "pandas>=1.5.0",
        "faiss-cpu>=1.7.0",
        "sentence-transformers>=2.2.0",
    ],
    entry_points={
        "console_scripts": [
            "aivia=aivia.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
