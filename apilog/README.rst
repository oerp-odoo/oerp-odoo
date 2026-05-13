API Logger
##########

Base module to log incoming and outgoing requests within odoo.

It currently exposes ``WSGI`` incoming requests for logging, but it can
be used to be extended to log different kind request sources.

You can specify expression to match specific requests that are
happening, so you would be able to save logs for requests you are
interested.

Expression can use ``inp`` object which consists of:

* endpoint
* verb
* status_code

It also can use ``re_match`` function, which is ``match`` function from
``re`` module.

Logs can be rotated by specifying maximum number of logs and/or days to
keep per API Log Configuration.

You can also specify labels either generally for all logs matching
configuration or also extra labels matching specific pattern within
a call (after it matched log configuration).

Contributors
------------

* Author: Andrius Laukavičius <dev@timefordev.com>
* Silvija Butko
