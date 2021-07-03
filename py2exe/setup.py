"""
Make sure you do pip install py2exe

This is to further prevent people from getting the webhook and whatever.

"""
from distutils.core import setup
import py2exe

setup(console=['main.py'])
