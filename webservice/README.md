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
        sudo bash
        sudo -u postgres
        psql
        CREATE ROLE <user_name> SUPERUSER;
        CREATE DATABASE oceanpostgres;
        \q
    
    Now database is created. Modify your settings_local.py
    and replace postgres credentials

* ***psycopg***
    Package for postgres
    
        sudo pip install psycopg2


* ***pillow***
	(For user pictures):
	
        sudo pip install pillow
    

## Running webservice

* In order to run webservice run neo4j database

        sudo neo4j start

* If it is your first start

        python manage.py syncdb
    
* And finally
    
        python manage.py runserver <port>
        
* Note: to log in go to /admin page and log in (for testing)


## Directories in project, explained

* templates - all templates (added in TEMPLATES_DIR)

* static - reference https://docs.djangoproject.com/en/dev/howto/static-files/ , all CSS/img files served by webservice

* rss - temporary application handling rss requests (show_news)

