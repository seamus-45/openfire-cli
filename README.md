openfire-cli
============

Openfire RestAPI command line interface

Features
--------
* List, add, update or delete users. Subscribe on groups. Manage lockouts and roster.
* List, add, update or delete rooms. List room users or grant roles.
* List, add, update or delete groups.
* List or close user sessions. View concurrent sessions.
* List, add, update or delete system properties.
* Send broadcast message or get count of unread messages of the user.

*Some features will not work if [Openfire](http://www.igniterealtime.org/projects/openfire/) version less than 3.10.0*

TODO
----
* Managing shared groups
* Delayed lockout

Installation
------------
Install dependencies:

      $ pip install docopt==0.6.2
      $ git clone git://github.com/seamus-45/openfire-restapi.git
      $ cd openfire-restapi
      $ python setup.py install

Install openfire-cli:

      $ git clone git@github.com:seamus-45/openfire-cli.git
      $ cd openfire-cli
      $ chmod +x openfire-cli.py
      $ echo "host = 'http://example.org:9090'" > config.py
      $ echo "secret = 'SuPeRsEcRet'" >> config.py

*Secret key will be found in `Server Settings` of REST API Plugin*
