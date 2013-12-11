Ocean Webservice
================

## Depedencies

In order to run Ocean webservice you need to install:



* ***neo4j***

    Install neo4j 1.9 not 2.0! (Gremlin plugin issues)

    *WARNING*: Everything fails if you do not have initialized database (it is
an error in neo4django you have to have at least one node in graph).

    Run

        python scripts/ocean_exemplary_data.py

    and press enter. It will populate graph database with exemplary data

* ***neo4django***

	(For neo4j-django integration):

		pip install neo4django
        pip install py2neo

	*WARNING:* During the installation your django might get downgraded.
	* Django >= 1.3, <1.5 (1.4.9, as for 2013-10-30)

* ***postgresql***

    	sudo apt-get install postgresql

* ***psycopg***
    Package for postgres

    Ubuntu:

        sudo pip install psycopg2


* ***pillow***
	(For user pictures):

        sudo pip install pillow


## Running webservice

* In order to run webservice run neo4j database

        sudo neo4j start

* Run postgresql database

    **Ubuntu**:

        sudo apt-get install postgresql
        sudo bash
        sudo -u postgres
        psql
        CREATE ROLE <user_name> SUPERUSER;
        CREATE DATABASE oceanpostgres;
        \q

    **Other Linux**:

    If you have an old database cluster that you don't need any more:

        sudo rm -rf /var/lib/postgres/data/

    Above directory should be a PostgreSQL data directory (PGDATA enviroment variable).

    Initialize a database cluster:

        su - postgres -c "initdb -D '/var/lib/postgres/data'"

    Start PostgreSQL database server:

        postgres -D /var/lib/postgres/data

    or (without systemd):

        sudo /etc/init.d/postgresql-8.3

    or (with systemd):

        systemctl start postgresql

    add service startup with boot (with systemd):

        systemctl enable postgresql

    Perform:

        sudo bash
        sudo -u postgres

    or:

        su
        su - postgres

    and:

        psql
        create role <user_name> with login superuser;
        create database oceanpostgres;
        \q


    Now database is created. Modify your settings_local.py
    and replace postgres credentials

* If it is your first start

        python manage.py syncdb

* And finally

        python manage.py runserver <port>

* Note: to log in go to /admin page and log in (for testing)


## Directories in project, explained

* templates - all templates (added in TEMPLATES_DIR)

* static - reference https://docs.djangoproject.com/en/dev/howto/static-files/ , all CSS/img files served by webservice

* rss - temporary application handling rss requests (show_news)


## Side notes and issues

* Neo4j database restarting

    Sometimes database gets corrupted. You can erase all nodes using ocean_exemplary_data.py. If you want to purge database it can be done by (check neo4j home by dpkg -L neo4j)

        sudo rm /var/lib/neo4j/data/graph.db/* -r -f

* Django models attribute changes

    When working on webservice, rarely models definitions would change. If so, confilcts could happen like:

        DatabaseError: column rss_userprofile.show_email does not exist

    (in below case a column named `show_email` has been added to model `UserProfile`.)
    (This error appears when dealing with old models instances using new definitions)

    Current *risky* **workaround** is to `drop table rss_userprofile;` from within PostgreSQL console.

