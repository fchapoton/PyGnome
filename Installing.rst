

Building / Installing PyGNOME with the conda package manager
============================================================


TL;DR
=====

If you are already set up to use conda, then it's as simple as:

Add the conda-forge channel::

    > conda config --add channels conda-forge

Create an environment for PyGNOME::

    conda create -n gnome --file conda_requirements.txt

Activate the gnome environment::

    conda activate gnome

Build the gnome package::

    > python setup.py develop

You now should be good to go, but to make sure:

Run the tests::

    > cd PyGnome/py_gnome/tests/unit_tests
    > py.test --runslow


All the details
===============

`Anaconda <https://store.continuum.io/cshop/anaconda/>`__ is a Python
distribution that has most of the difficult-to-build packages that
``PyGNOME`` needs already built in. Thus it's a nice target for running
GNOME on your own system. "conda" is the packaging manager used to manage the system.

PyGNOME CAN be used with any Python distribution, but you will need to find or build a number of packages that are not easy to manage. If you are familiar with complex python packaging, then you can probably make it work. But conda makes it much easier, and that's what we use ourselves, and support that use.

Anaconda vs miniconda:
----------------------

`Anaconda <https://store.continuum.io/cshop/anaconda/>`__ provides a fairly complete python system for computational programming -- it is a large install, but comes with a lot of nice stuff pre-packaged that all works together.

`miniconda <http://conda.pydata.org/miniconda.html>`__ is a much smaller install -- it provides only Python and the conda package management system. You can install miniconda, and then install only the packages you need to run ``PyGNOME``.

Either will work fine with ``PyGNOME``.

**NOTES:**

PyGNOME requires Python version 3.8 or greater.

Anaconda (and miniconda) can be installed in either single-user or multi-user mode:

https://docs.continuum.io/anaconda/install

We (and Anaconda) recommend single-user mode (Select an install for “Just Me”) -- that way, administrator privileges are not required for either initial installation or maintaining the system.

Windows:
........

You want the Windows 64 bit Python 3 version. Installing with the
defaults works fine. You probably want to let it set the PATH for you --
that's a pain to do by hand.


OS-X:
.....

Anaconda provides a 64 bit version -- this should work well with
``PyGNOME``. Either the graphical installer or the command line one is
fine -- use the graphical one if you are not all that comfortable with
the \*nix command line.

Linux:
......

The Linux 64bit-python3.8 is the one to use.

We do not support 32 bit on any platform.

conda
-----

`conda <http://conda.pydata.org/docs/intro.html>`__ is the package
manager that Anaconda is built on. So when working with Anaconda, you
use the conda package manager for installing conda packages. ``pip``
can also be used within conda, but it's best to use use conda for as much as you can.

As a rule, if you need a new package, you should try to conda install it, and then, if there is not conda package available, you can pip install it.

We have made sure that every package you need for PyGNOME is available for conda.

conda-forge
...........

Conda-Forge (https://conda-forge.org/) is a community  project that supplies a huge number of packages for the conda package manager. We have tried to assure that everything you need to run PyGNOME is available via the conda-forge channel.

Setting up
..........

Install: `Anaconda <https://www.continuum.io/downloads>`__

or alternatively: `Miniconda <http://conda.pydata.org/miniconda.html>`__

Once you have either Anaconda or Miniconda installed, the rest of the
instructions should be the same.


Update your (new) system
........................

Once you have Anaconda or miniconda installed, you should start by
getting everything up to date, as sometimes packages have been updated
since the installer was built.

First, update the conda package manager itself:

Enter the following on the command-line::

    > conda update conda

Setting up anaconda.org channels
................................

`anaconda.org <http://anaconda.org>`__ is a web service for hosting conda packages for download. The way this is done is through
anaconda "channels", which can be thought of simply as places on
``anaconda.org`` where collections of packages are bundled together by the
people hosting them.

Many of the dependencies that ``PyGNOME`` requires come out of the box
with Anaconda (or the conda "defaults" channel), but a few don't.

**The "conda-forge" project:**

https://conda-forge.github.io/

Is a community project to build a wide variety of packages for conda --
it should support everything that PyGNOME needs.


Adding another channel to conda:
................................

To make it easy for your install to find conda-forge packages, they should be added to your conda configuration:

Add the conda-forge channel::

    > conda config --add channels conda-forge

When you add a channel to conda, it puts it at the top of the list.
So now when you install a package, conda will first look in conda-forge,
and then in the default channel. This order should work well for PyGNOME.

You can see what channels you have with::

    > conda config --get channels

It should return something like this::

    --add channels 'defaults'   # lowest priority
    --add channels 'conda-forge'   # highest priority

In that order -- the order is important

conda environments
------------------

The conda system supports isolated "environments" that can be used to
maintain different versions of various packages. For more information
see:

http://conda.pydata.org/docs/using/envs.html

NOTE: We highly recommend that you use an environment for GNOME.

If you are only going to use Python / conda for PyGNOME, then you could use the base environment. However, pyGNOME needs a number of specific package versions, so it is best to keep it separate from any other work you are doing.

(NOTE: you can do these steps with the Anaconda Navigator GUI if you have that installed)

Create an environment for PyGNOME::

    conda create -n gnome --file conda_requirements.txt

This will create an environment called "gnome" with Python itself and everything that it needs to run -- it will be quite a bit, so may take a while.

To use that environment, you activate it with::

    conda activate gnome


and when you are done, you can deactivate it with::

    conda deactivate


After activating the environment, you can proceed with these instructions,
and all the packages ``PyGNOME`` needs will be installed into that environment and kept separate from your main Anaconda install.

You will need to activate the environment any time you want to work with
``PyGNOME`` in the future


Download GNOME
--------------

Once you have conda (or an environment) set up, you can compile and install ``PyGNOME``. PyGNOME is not currently available as a conda package, as it is under active development, and many users will need access to the source code.

You will need the files from the ``PyGNOME`` sources. If you
have not downloaded it yet, it is available here:

https://github.com/NOAA-ORR-ERD/PyGnome

You can either download a zip file of all the sources and unpack it, or
you can "clone" the git repository. If you clone the repository, you will
be able to update the code with the latest version with a simple command,
rather than having to re-download the whole package.


Downloading a single release
----------------------------

zip and tar archives of the PyGnome source code can be found here:

https://github.com/NOAA-ORR-ERD/PyGnome/releases

This will get you the entire source archive of a given release, which is a fine way to work with PyGnome. However, if you want to be able to quickly include changes as we update the code, you may want to work with a git "clone" of the source code instead.

Cloning the PyGNOME git repository
----------------------------------


git
...

You will need a git client:

Linux:
  it should be available from your package manager::

    $ apt_get install git
    or
    $ yum install git

OS-X:
  git comes with the XCode command line tools:

  http://osxdaily.com/2014/02/12/install-command-line-tools-mac-os-x/

Windows:
  the "official" git for Windows installer is a good bet:

  https://git-for-windows.github.io/

Once you have the client, it's as easy as::

  $ git clone https://github.com/NOAA-ORR-ERD/PyGnome.git

This will create a PyGnome directory with all the code in it.


Setting up conda
----------------

The conda packages required by ``PyGNOME`` are listed in the file
``conda_requirements.txt`` in the top directory of the project.

Once you have the source code, you can create an environment for PyGNOME::

    conda create -n gnome --file conda_requirements.txt

This will create an environment called "gnome" with Python itself and everything that it needs to run -- it will be quite a bit, so may take a while.

a activate gnomeTo use that environment, you activate it with::

    cond

and when you are done, you can deactivate it with::

    conda deactivate

If you don't want to create and environment (Or already have one), you can install what ``PyGNOME`` needs into an existing environment:

::

    > cd PyGnome  # or wherever you put the PyGnome project
    > conda install --file conda_requirements.txt


This should install all the packages required by ``PyGNOME``.

(make sure you are in the correct conda environment, and you have the
conda-forge channel enabled.)

If installing conda_requirements.txt fails:
...........................................

If you get an error about a particular package not being able to be installed, then conda will not install ANY of the packages in the file. We try hard to make sure everything is available on conda-forge. If however, a package of that particular version is missing, you can try:

Edit the conda_requirements.txt file and comment out the offending package by putting a "#" at the start of the line::

    ...
    scipy>=0.17
    py_gd>=0.1.5
    # libgd>=2.2.2
    gsw>=3.0.3
    ...

That will disable that particular package, and hopefully everything else will install.

You can then try installing the offending package without a version specification::

    > conda install libgd

And it may work for you.


The ADIOS Oil Database
----------------------

If you want to use PyGNOME with "real oil", rather than inert particles, you will need NOAA's adios_db package from the ADIOS Oil Database Project:

https://github.com/NOAA-ORR-ERD/adios_oil_database

This will allow you to use the JSON oil data format downloadable from NOAA's ADIOS Oil Database web app:

https://adios.orr.noaa.gov/oils/

The ``adios_db`` package is under active development along with ``PyGNOME``, so you are best off downloading the sources from gitHub and installing it from source -- similar to ``PyGNOME``.

The latest releases (of the same branch) of each should be compatible.

cloning the repository ::

  $ git clone https://github.com/NOAA-ORR-ERD/adios_oil_database.git

Installing its dependencies::

  $ cd adios_db
  $ conda install --file conda_requirements.txt


Installing the package::

  $ pip install ./

(or ``pip install -e ./`` to get an "editable" version)


Testing the adios_db install::

  $ pytest --pyargs oil_library

(you may need to ``conda install pytest`` to get that command)

you should see a lot of output, and then something like::

  ====== 1130 passed, 192 skipped, 1 warning in 50.78s ======

when done.

Compilers
---------

To build ``PyGNOME``, you will need a C/C++ compiler. The procedure for
getting the compiler tools varies with the platform you are on.

OS-X
....

The system compiler for OS-X is XCode. It can be installed from the App
Store.

*Note: it is a HUGE download.*

[you may be able to install only the command line tools -- Apple keeps changing its mind]

After installing XCode, you still need to install the "Command Line
Tools".  XCode includes a new "Downloads" preference pane to install
optional components such as command line tools, and previous iOS
Simulators.

**NOTE:** This may be slightly different on different versions of OS-X
and XCode -- google is your friend.

To install the XCode command line tools: - Start XCode from the
launchpad - Click the "XCode" dropdown menu button in the top left of
the screen near the Apple logo - Click "Preferences", then click
"Downloads". - Command Line Tools should be one of the downloadable
items, and there should be an install button for that item. Click to
install.

Once the command line tools are installed, you should be able to build
``PyGNOME`` as described below.


Windows
.......

For compiling python extensions on Windows with python3 it is best to use the

Microsoft the Visual Studio 2019 Build Tools. They should be available here:

https://visualstudio.microsoft.com/downloads/

The free "Community" version should be fine.


Linux
.....

Linux uses the GNU gcc compiler. If it is not already installed on your
system, use your system package manager to get it.

-  apt for Ubuntu and Linux Mint
-  rpm for Red Hat
-  dpkg for Debian
-  yum for CentOS
-  ??? for other distros

Building ``PyGNOME``
.....................

At this point you should have all the necessary third-party
tools in place.

Right now, you'll need to build ``PyGNOME`` from source.

And it is probably best to build a "develop" target for your ``PyGNOME`` package if you plan on developing or debugging the ``PyGNOME`` source code
(or updating the source code from gitHub).

Building the "develop" target allows changes in the python code
to be immediately available in your python environment without re-installing.

Of course if you plan on simply using the package, you may certainly
build with the "install" target. Just keep in mind that any updates to
the project will need to be rebuilt and re-installed in order for
changes to take effect.

There are a number of options for building:

::
    > python setup.py develop

builds and installs the gnome module development target.

::

    > python setup.py cleanall

cleans files generated by the build as well as files auto-generated by
cython. It is a good idea to run ``cleanall`` after updating from the
gitHub repo -- particularly if strange errors are occurring.

You will need to re-run ``develop`` or ``install`` after running ``cleanall``


Testing ``PyGNOME``
--------------------

We have an extensive set of unit and functional tests to make sure that
``PyGNOME`` is working properly.

To run the tests::

    > cd PyGnome/py_gnome/tests/unit_tests
    > py.test

and if those pass, you can run::

    > py.test --runslow

which will run some more tests, some of which take a while to run.

Note that the tests will try to auto-download some data files. If you
are not on the internet, this will fail. And of course if you have a
slow connection, these files could take a while to download. Once the
tests are run once, the downloaded files are cached for future test
runs.

What if some tests fail?
........................

We do our best to keep all tests passing on release versions of the package. But sometimes tests will fail due to the setup of the machine they are being run on -- package versions, etc. So the first thing to do is to make ure you have installed the dependencies as specified.

But ``gnome`` is large package -- hardly anyone is going to use all of it. So while we'd like all tests to pass, a given test failure may not be an issue for any given use case. It's a bit hard to know whether a given test failure will affect your use case, but if you look at the name of the tests that fail, you might get a hint. For example, if any of the tests fail under ``test_weathering``, and you are not doing and oil weathering modeling, you don't need to worry about it.

In any case, you can try to run your use case, and see what happens.


Running scripts
---------------

There are some example scripts in the ``scripts`` directory. You should be able to run these scripts in the same way as any Python script (with an IDE such as Spyder or PyCharm, or at the command line).

To run a script on the command line:

::

    cd py_gnome/example_scripts


If you are using a conda environment:

    source activate gnome

or on Windows::

    activate gnome

Run the script::

    python script_boston.py

Each of the scripts exercises different features of PyGNOME -- they are hopefully well commented to see how they work.





