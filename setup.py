from setuptools import setup, find_packages

setup(
    name='abwest-adaptive-learning',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django==4.2.11',
        'pymongo==4.6.1',
        'djangorestframework==3.14.0',
        'djangorestframework-simplejwt==5.3.0',
        'django-cors-headers==4.3.1',
        'python-dotenv==1.0.1',
        'whitenoise==6.6.0',
        'gunicorn==21.2.0',
    ],
)