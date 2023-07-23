/** @odoo-module **/

import "website_sale.website_sale";
import publicWidget from "web.public.widget";

publicWidget.registry.WebsiteSale.include({
    events: _.extend({}, publicWidget.registry.WebsiteSale.prototype.events, {
        'change input[name="vat"]': "_onChangeVat",
    }),
    _onChangeVat: function () {
        if (!this.$(".checkout_autoformat").length) {
            return;
        }
        this._changeVat();
    },
    _changeVat: function () {
        const vat = $('input[name="vat"]').val();
        if (!vat) {
            return;
        }
        this._rpc({route: "/shop/vies_data/" + vat}).then(function (data) {
            if (Object.keys(data).length) {
                const vals = data.vals;
                if (vals.name) {
                    $('input[name="company_name"]').val(vals.name);
                }
                if (vals.street) {
                    $('input[name="street"]').val(vals.street);
                }
                if (vals.country_id) {
                    const country_selection = $('select[name="country_id"]');
                    const country_id = vals.country_id;
                    country_selection
                        .children(`option[value="${country_id}"]`)
                        .prop("selected", true);
                    country_selection.change();
                }
            }
        });
    },
});
