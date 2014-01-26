NORB-Rocket-Predictor
=====================

Advanced prediction software to model the trajectory of a rocket based on many variable factors. 
This is an on-going project.


The software currently does the following:

1. Allows user to specify rocket mass, frontal area and drag coefficient of rocket, and desired rocket motor.
2. The software then produces three graphs: altitude/time, drag/time, and thrust/time. 



Upon completion, this software will perform as described here: http://www.norb.co.uk/projects/rocket-trajectory-predictor/


Note
====

To run this for yourself, you need to ensure that you have the following Python modules installed:

1. Matplotlib
2. python-dateutil
3. numpy
4. pyparsing
5. six


All can be found here: http://www.lfd.uci.edu/~gohlke/pythonlibs/ but for Linux users, just use pip.

ALSO IMPORTANT: This software will not run properly unless all the text files for the motors are located in the Python directory in the C drive. I'm currently working on adapting this software to run on Python 3.3 as well as Python 2.7.
