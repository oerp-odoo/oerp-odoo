odoo.define('web_no_quick_create.no_create', function(require) {
    "use strict";

    var relational_fields = require('web.relational_fields');
    var session = require('web.session');

    relational_fields.FieldMany2One.include({
        init: function() {
            this._super.apply(this, arguments);
            if (session.user_context['rel_field_quick_create_disabled']) {
                this.can_create = false;
            };
        },
    });
});
