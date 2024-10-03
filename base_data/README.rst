Find and Use data by specific keys
##################################

When data record is matched, specified ``Defaults`` are used. If there
are ``Options`` specified, these can be matched via ``frozenset([('key1', 'val1')..])``
options. If it matches key/val pair, ``Data`` defined on option is used in data
dictionary. If it matches same keys as ``Defaults``, it will overwrite it.

Contributors
------------

* Author: Andrius Laukavičius (timefordev)
