API Base
########

Base API module to use for specific API implementations:

* ``/api/base/partners`` endpoint to create partners.
* Can use ``api_base.no_html_exception_description`` config parameter to
  return exception description as pure text instead of wrapped in HTML (which is
  done by werkzeug by default).

Contributors
============

* Andrius Laukavičius (timefordev)
