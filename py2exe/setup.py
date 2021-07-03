"""
Make sure you do pip install py2exe, then when you're in the directory in command prompt type python <filename>.py py2exe

This is to further prevent people from getting the webhook and whatever by using a python intepreter through a dll so no one actually needs python installed.
"""
from distutils.core import setup
import py2exe

setup(console=['main.py'])
