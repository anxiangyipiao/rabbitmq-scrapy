# -*- coding: utf-8-*-
from setuptools import setup
import os


here = os.path.abspath(os.path.dirname(__file__))


setup(
    # 以下为必需参数
    name='rabbitmq_scrapy',  # 模块名
    version='1.0',  # 当前版本
    description='Rabbitmq for Distributed scraping',  # 简短描述
    long_description_content_type='text/markdown',
    license='MIT',
    install_requires=[
        'pika',
    ],
    packages=['rabbitmq_scrapy'],
    package_dir={'': 'src'}
)

