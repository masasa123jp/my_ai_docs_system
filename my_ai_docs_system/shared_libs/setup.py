from setuptools import setup, find_packages

setup(
    name='shared_libs',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests',  # 必要な依存ライブラリをここに追加
    ],
    author='Your Name',
    author_email='your.email@example.com',
    description='Shared libraries for AI and RAG utilities',
    url='https://your-repo-url.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
