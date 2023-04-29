Website Sale - Vat Validation Fields
####################################

Improves the way VAT is validated via odoo website:

* Shows partner name when validation fails (instead of False)
* Validates as if partner has ``is_company=True``. This allows to do VIES VAT
  validation via website as well.

Contributors
============

* Andrius Laukavičius (timefordev)
