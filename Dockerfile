FROM focusate/odoo:15.0
COPY --chown=odoo:odoo ./ /opt/odoo/projects/oerp-odoo
RUN pip3 install --no-cache-dir -r /opt/odoo/projects/oerp-odoo/requirements.txt
