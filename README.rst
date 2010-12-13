===================
FUSQL Linux Version
===================

Main version of the project, done to use it on a linux
machine.

Fusql it's a interface of a SQL database (sqlite for now) as a file system,
where you have tables as folders and ini formated files as rows.
Inside a file you will find the column names and it's value.

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

will be visualized as the following directory tree:

::
    /

    |--- users
      |--- 1.ini

      |--- 2.ini


and 1.ini will be like:

::
    id = 1
    username = j0hn
    password = secret
    name = Gonzalo
    lastname = Garcia
    address = example
    phone = 1234
    city = Cordoba

