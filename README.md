# Catalog project

The main scope is to create a full item catalog with authentication/authorization through a service, in this case Google Oauth

## Usage
To run the program you need python 2 (tested with version 2.7.12). 

Required module are :
* flask
* sqlalchemy
* requests
* oauth2client
* random
* string
* httplib2
* json
* datetime

First step is to create an empty database called catalog
After that you need to run the db_setup.sql file to create the tables with some dummy data. 
```
psql -d catalog -a -f db_setup.sql
```
Inside the virtual machine run `python catalog.py` who will start the site available at [http://localhost:5000](http://localhost:5000) .

The categories are listed on the left, items at center. 

If logged in, there are links to edit and delete any category or items and a link to create a new one. 

On the home page are listed the 10 most recent items.

Clicking a category name will show all items for that category, clicking an item will show his details.

Adding /JSON at the end of a category or item detail will return json data for that category or item.
To simplify python code various views has been created:

The function to login via Google plus has been implemented through the course so the will be pretty identical to that.
