# SD<sup>2</sup>: Software Defined Software Development™
The Software Defined Software Development Process aka SD<sup>2</sup> is 
a modern Software Development approach that aims to simplify the 
complexity that usually accompanies working with multiple projects 
each with multiple branches. SD<sup>2</sup> relies heavily on **one** text 
file that describes a developer's development environments and containers 
that isolate the different environments. It also seperates the editing 
environment from the environment where compilation and testing takes place. 
In some sense, we bring the advantages of a microserivces environment to 
the development phase even when you do not use microservices in production.

## Prerequisites
The tools have been tested on MacOS and Ubuntu hosts. At a minimum you 
need one machine (e.g. a MacOS notebook) with docker installed that will
 play the role of both the editor and the development machine.

1. Editor Machine Requirements
   1. Python 2.7 with additional packages: python_hosts jinja2
1. Development Machine Requirements
   1. docker 


## What is not covered by SD<sup>2</sup>

1. Bring your own editor/IDE. We are agnostic how you edit your source code.
1. Bring your own container images. We do not provide tools to generate
 docker images, we expect that are already available and published in 
 a local or remote repository.

More coming soon...
