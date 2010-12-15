FUSQL
===================

Main version. Developed under linux. (and now working with OS X!) 

Fusql works as a interface between a relational database (sqlite for
now) and a filesystem. Each table is represented as a directory and each
row is represented as a collection of files.

We're supporting creating / deleting and modifying tables and table
structures as a experimental features. This took about 6 hours in a
sunday. (and we keep doing it)

Example:
========

A database like:

    +------+----------+----------+---------+----------+---------+-------+---------+
    | id   | username | password | name    | lastname | address | phone | city    |
    +------+----------+----------+---------+----------+---------+-------+---------+
    | 1    | j0hn     | secret   | Gonzalo | Garcia   | example | 1234  | Cordoba |
    +------+----------+----------+---------+----------+---------+-------+---------+
    | 2    | nassty   | secret2  | Mariano | Garcia   | example | 4321  | Cordoba |
    +------+----------+----------+---------+----------+---------+-------+---------+

will be visualized as the following :
::
    $ ls
    users
    $ ls users
    1 2
    $ ls users/1 
    id.int username.txt password.txt name.txt lastname.txt address.txt phone.txt city.txt
    $ cat users/1/username.txt
    j0hn

Also tweaking the table names you can get a pseudo-dynamic webapp. 

* The cols named "start" are  mapped to "index.html"
* the cols named "style" are mapped to "style.css"
* and the columns named "functions" are mapped to "functions.js". 
  
You can run a web browser on top of that and enjoy:
::
    $ mkdir tmp
    $ python fusql.py -f tmp &
    [1] 90210
    $ cd tmp
    $ python -m SimpleHTTPServer &
    [2] 1337
    Serving HTTP on 0.0.0.0 port 8000 ...
    $ curl localhost:8000/pages/1/index.html
    localhost - - [31/Feb/1337 55:76:49] "GET /pages/1/index.html HTTP/1.1" 200 -
    <html>
    <head>
        <link type="text/css" rel="stylesheet" href="style.css" />
        <script type="text/javascript" src="functions.js"></script>

    </head>
    <body>
    <h1 class="header">Hello</h1>
    <p class="content"> this is just a test app</p>
    </body>
    </html>
    $ sudo umount tmp


We're awesome. 
