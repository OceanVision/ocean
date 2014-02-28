Ocean Webservice
================

## Depedencies

In order to run Ocean webservice you need to install necessary python modules:

	`pip install -r requirements.txt`
	
In case of dependency problems it is better to use virtualenv (see wiki page on Deployment).



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


---

## Development issues

Please refer to this section in case of any questions. Feel free to add your own essential Q&A.


### 1. Neo4j database restarting

Sometimes database gets corrupted. You can erase all nodes using ocean_exemplary_data.py. If you want to purge database it can be done by (check neo4j home by dpkg -L neo4j)

    sudo rm /var/lib/neo4j/data/graph.db/* -r -f

### 2. Django models attribute changed issue

When working on webservice, rarely models definitions would change. If so, confilcts could happen like:

    DatabaseError: column rss_userprofile.show_email does not exist

    (in below case a column named `show_email` has been added to model `UserProfile`.)
    (This error appears when dealing with old models instances using new definitions)

Current *temporary* workaround (unless we start to use South) is to `drop database`:

Get root rights:

    $ su

Get postgres user rights:

    # su -- postgres

Run PostgreSQL console:

    # psql

Inside console execute following commands:

    postgres=# drop database oceanpostgres;
    postgres=# create database oceanpostgres;
    postgres=# \q

Exit root:

    # exit
    # exit

Enter `webservice` directory and perform:

    $ python2 manage.py syncdb

Crete Django user with the same login as before `drop` (don't forget to enter e-mail adress).
