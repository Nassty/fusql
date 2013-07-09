===================
FUSQL
===================

Main version. Developed under linux. (and now working with OS X!) 

Fusql works as a interface between a relational database (sqlite for
now) and a filesystem. Each table is represented as a directory, each
row is represented as a folder inside a table folder and each column
is represented as a file inside a row folder.

Actually Supported
------------------

fusql now supports:

* list tables, rows and columns
* create/delete tables creating or deleting folders on the root directory
* create/delete rows creating or deleting folders inside a table folder
* create columns creating a file inside any row (it will update the other rows)
* rename tables or rows just renaming the respective folder
* view a cell content just reading the content of the respective column inside a row
* write on column files (still a little buggy)
* binary file support it's still experimental

Instalation and Running
-----------------------

To run it, make sure you have Fuse installed, and python bindings
(check http://fuse.sourceforge.net/) and for python bindings in ubuntu
use the package python-fuse, for other distros you should investigate.
Once you have that you can run it using:
::
    $ python fusql.py -f mnt_folder


And if you don't want to view the debug
::
    $ python fusql.py mnt_folder


To unmount it you can run
::
    $ fusermount -u mnt_folder


License
-------

Fusql it's now using DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
to read more about it reed file LICENSE

Example:
--------

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


Cool usage of this project
--------------------------
Tweaking the table names you can get a pseudo-dynamic webapp. 

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
