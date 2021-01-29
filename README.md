#  Introduction
Welcome to GAIR - Geoportal of Adriatic-Ionian Region

The Geo data portal of Adriatic Ionian Region (GAIR) is a community-based, open source portal based on GeoNode     ([http://geonode.org/](http://geonode.org/)),  a web-based Content       Management System (CMS) for developing geospatial  information systems       (GIS) and for deploying spatial data infrastructure  (SDI).
GAIR provides access to numerous datasets related to coastal and  marine       areas and to several modules for Integrated Coastal Zone  Management       (ICZM) and Maritime Spatial Planning (MSP) analysis and risk  assessment.

![Build Status](https://www.portodimare.eu/static/docs/_images/portodimare_home.png)

In particular, the already implemented tools are:
      - Module for Cumulative Effects Assessment (CEA)
      - Module for Maritime Use Synergy and Conflict Analysis Tool (MUSC)
      - Module for Supporting Allocated Zones for Aquaculture (AZA)
      identification
      - Module for particle/conservative contaminants dispersion (PAR TRAC)
      - Module for Coastal Oil Spill Vulnerability Assessment
      - Module for Small Scale Fishery Footprint (SSF)
      - Module on Medium Scale Fishery Footprint (MSF) & Cumulative Effects
      Assessment on SSF & MSF.

![Build Status](https://www.portodimare.eu/static/docs/_images/MUC_matrix_pconflict.png)
sostituito a quello attuale visto
The Geoportal capitalizes data from other projects (e.g. Shape,  Adriplan)      and integrates existing databases/portals developed at  European and      national level. GAIR thus represents a relevant and original instrument      that improves  concretely the support to  transparent and efficient      decision-making  processes and transnational cooperation between the      Adriatic and Ionian  Region Countries on maritime and marine governance      and services and on  the implementation of ICZM/MSP processes. For the      same reason, GAIR is  an important support to the EUSAIR Action Plan      implementation,  cross-cutting to the 4 Pillars of the Strategy.

GAIR is developed under _geoPORtal of TOols & Data for sustaInable      Management of coAstal and maRine Environment_       ([https://portodimare.adrioninterreg.eu/](https://portodimare.adrioninterreg.eu/)) _ADRION_ programme.


# Release
Developer Workshop
------------------

Available at::

    http://geonode.org/dev-workshop


Create a custom project
-----------------------
This is based on a GeoNode template project. Generates a django project with GeoNode support.

Note: You can call your geonode project whatever you like following the naming conventions for python packages (generally lower case with underscores (``_``). In the examples below, replace ``my_geonode`` with whatever you would like to name your project.

Using a Python virtual environment
++++++++++++++++++++++++++++++++++

To setup your project using a local python virtual environment, follow these instructions:

1. Prepare the Environment

  .. code:: bash

    git clone https://github.com/GeoNode/geonode-project.git -b 2.10.x
    mkvirtualenv my_geonode
    pip install Django==1.11.21

    django-admin startproject --template=./geonode-project -e py,rst,json,yml,ini,env,sample -n Dockerfile my_geonode

    cd my_geonode

2. Setup the Python Dependencies

  .. code:: bash

    pip install -r requirements.txt --upgrade
    pip install -e . --upgrade

    GDAL_VERSION=`gdal-config --version`
    PYGDAL_VERSION="$(pip install pygdal==$GDAL_VERSION 2>&1 | grep -oP '(?<=: )(.*)(?=\))' | grep -oh $GDAL_VERSION\.[0-9])"
    pip install pygdal==$PYGDAL_VERSION

    # Using Default Settings
    DJANGO_SETTINGS_MODULE=my_geonode.settings paver reset
    DJANGO_SETTINGS_MODULE=my_geonode.settings paver setup
    DJANGO_SETTINGS_MODULE=my_geonode.settings paver sync
    DJANGO_SETTINGS_MODULE=my_geonode.settings paver start

    # Using Custom Local Settings
    cp my_geonode/local_settings.py.sample my_geonode/local_settings.py

    vim my_geonode/wsgi.py
    --> os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_geonode.local_settings")

    DJANGO_SETTINGS_MODULE=my_geonode.local_settings paver reset
    DJANGO_SETTINGS_MODULE=my_geonode.local_settings paver setup
    DJANGO_SETTINGS_MODULE=my_geonode.local_settings paver sync
    DJANGO_SETTINGS_MODULE=my_geonode.local_settings paver start

3. Access GeoNode from browser::

    http://localhost:8000/

.. note:: default admin user is ``admin`` (with pw: ``admin``)

Start your server
-----------------

You need Docker 1.12 or higher, get the latest stable official release for your platform.

1. Prepare the Environment

  .. code:: bash

    git clone https://github.com/GeoNode/geonode-project.git -b 2.10.x
    mkvirtualenv my_geonode
    pip install Django==1.11.21

    django-admin startproject --template=./geonode-project -e py,rst,json,yml,ini,env,sample -n Dockerfile my_geonode

    cd my_geonode

2. Run `docker-compose` to start it up (get a cup of coffee or tea while you wait)

Remember to update "wsgi.py" in case you are using "local_settings"
vim my_geonode/wsgi.py
--> os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_geonode.local_settings")

  .. code:: bash

    docker-compose build --no-cache
    docker-compose up -d

  .. code-block:: none

    set COMPOSE_CONVERT_WINDOWS_PATHS=1

before running docker-compose up

3. Access the site on http://localhost/

If you want to run the instance for development
-----------------------------------------------

Use dedicated docker-compose files while developing
+++++++++++++++++++++++++++++++++++++++++++++++++++

.. note:: In this example we are going to keep localhost as the target IP for GeoNode

.. code:: bash

  docker-compose -f docker-compose.development.yml -f docker-compose.development.override.yml up

How to debug
++++++++++++

.. note:: We are supposing to use IPDB for debugging which is already available as package from the container

1. Stop the container for the "django" service::

  .. code:: bash

    docker-compose stop django

2. Run the container again with the option for service ports::

  .. code:: bash

    docker-compose run -e DOCKER_ENV=development --rm --service-ports django python manage.py runserver --settings=my_geonode.settings 0.0.0.0:8000

3. Access the site on http://localhost/

If you set an IPDB debug point with ``import ipdb ; ipdb.set_trace()`` then you should be facing its console and you can see the django
server which is restarting at any change of your code from your local machine.

If you want to run the instance on a public site
------------------------------------------------

Preparation of the image (First time only)
++++++++++++++++++++++++++++++++++++++++++

.. note:: In this example we are going to publish to the public IP http://123.456.789.111

.. code:: bash

  vim docker-compose.override.yml
    --> replace localhost with 123.456.789.111 everywhere

Startup the image
+++++++++++++++++

.. code:: bash

  docker-compose up --build -d


To Stop the Docker Images
-------------------------

.. code:: bash

  docker-compose stop


To Fully Wipe-out the Docker Images
-----------------------------------

.. warning:: This will wipe out all the repositories created until now.

.. note:: The images must be stopped first

.. code:: bash

  docker system prune -a


Recommended: Track your changes
-------------------------------

Step 1. Install Git (for Linux, Mac or Windows).

Step 2. Init git locally and do the first commit:

    git init

    git add *

    git commit -m "Initial Commit"

Step 3. Set up a free account on github or bitbucket and make a copy of the repo there.

Hints: Configuring Requirements.txt
-----------------------------------

You may want to configure your requirements.txt, if you are using additional or custom versions of python packages.  For example::

    Django==1.11.21
    six==1.10.0
    django-cuser==2017.3.16
    django-model-utils==3.1.1
    pyshp==1.2.12
    celery==4.1.0
    Shapely>=1.5.13,<1.6.dev0
    proj==0.1.0
    pyproj==1.9.5.1
    pygdal==2.2.1.3
    inflection==0.3.1
    git+git://github.com/<your organization>/geonode.git@<your branch>


Hints: Using Ansible
--------------------

You will need to use Ansible Role in order to run the playbook.

In order to install and setup Ansible, run the following commands::

    sudo apt-get install software-properties-common
    sudo apt-add-repository ppa:ansible/ansible
    sudo apt-get update
    sudo apt-get install ansible

A sample Ansible Role can be found at https://github.com/GeoNode/ansible-geonode

To install the default one, run::

    sudo ansible-galaxy install GeoNode.geonode

you will find the Ansible files into the ``~/.ansible/roles`` folder. Those must be updated in order to match the GeoNode and GeoServer versions you will need to install.

To run the Ansible playbook use something like this::

    ANSIBLE_ROLES_PATH=~.ansible/roles ansible-playbook -e "gs_root_password=<new gs root password>" -e "gs_admin_password=<new gs admin password>" -e "dj_superuser_password=<new django admin password>" -i inventory --limit all playbook.yml


Configuration
=============

Since this application uses geonode, base source of settings is ``geonode.settings`` module. It provides defaults for many items, which are used by geonode. This application has own settings module, ``porto_di_mare.settings``, which includes ``geonode.settings``. It customizes few elements:
 * static/media files locations - they will be collected and stored along with this application files by default. This is useful during development.
 * Adds ``porto_di_mare`` to installed applications, updates templates, staticfiles dirs, sets urlconf to ``porto_di_mare.urls``.

Whether you deploy development or production environment, you should create additional settings file. Convention is to make ``porto_di_mare.local_settings`` module. It is recommended to use ``porto_di_mare/local_settings.py``.. That file contains small subset of settings for edition. It should:
 * not be versioned along with application (because changes you make for your private deployment may become public),
 * have customized at least ``DATABASES``, ``SECRET_KEY`` and ``SITEURL``.

You can add more settings there, note however, some settings (notably ``DEBUG_STATIC``, ``EMAIL_ENABLE``, ``*_ROOT``, and few others) can be used by other settings, or as condition values, which change other settings. For example, ``EMAIL_ENABLE`` defined in ``geonode.settings`` enables whole email handling block, so if you disable it in your ``local_settings``, derived settings will be preserved. You should carefully check if additional settings you change don't trigger other settings.

To illustrate whole concept of chained settings:
::
    +------------------------+-------------+-------------------------------+-------------+----------------------------------+
    |  GeoNode configuration |             |   Your application default    |             |  (optionally) Your deployment(s) |
    |                        |             |        configuration          |             |                                  |
    +========================|=============|===============================|=============|==================================+
    |                        | included by |                               | included by |                                  |
    |   geonode.settings     |     ->      |  porto_di_mare.settings    |      ->     |  porto_di_mare.local_settings |
    +------------------------|-------------|-------------------------------|-------------|----------------------------------+
    
# Credits, documentation and how to contribute
Developed with the support of Regione Emilia Romagna.

All issues on Github are public. So, if the issue is one that is fine to disclose publicly, you could report it via the issue tracker.
Securit issues must be addressed privately to portodimare@regione.emilia-romagna.it

-    Issue Tracker: https://github.com/RegioneER/portodimare-gair/issues
-    Source Code: https://github.com/RegioneER/portodimare-gair


Full documentation for end users is available online at https://www.portodimare.eu/static/docs/index.html

# License
GAIR is ©2021 PORTODIMARE / developed by Regione Emilia-Romagna 
Where third party code is included, a special licence notice is included following the rules defined in <https://reuse.software/spec/>.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. 
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
A copy of the GNU General Public License should be included along with this repository. If not, see <http://www.gnu.org/licenses>.

GAIR <https://www.portodimare.eu/> is the main output of the project PORTODIMARE, co-funded by the Interreg ADRION Programme <https://www.adrioninterreg.eu/>. 

[![Build Status](https://www.portodimare.eu/static/docs/_static/logo-adrion-portodimare.png)](https://github.com/RegioneER/portodimare-gair)

