===================
FUSQL Linux Version
===================

Main version. Developed under linux. 

Fusql works as a interface between a relational database (sqlite for
now) and a filesystem. Each table is represented as a directory and each
row is represented as a .ini file.

We're supporting creating / deleting and modifying tables and table
structures as a experimental features. This took about 6 hours in a
sunday.

We plan support OS X when we get the python-fuse bindings working. 


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
    1.ini 2.ini
    $ cat 1.ini
    id = 1
    username = j0hn
    password = secret
    name = Gonzalo
    lastname = Garcia
    address = example
    phone = 1234
    city = Cordoba

