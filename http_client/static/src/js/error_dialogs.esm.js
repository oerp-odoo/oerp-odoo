/** @odoo-module */

import {WarningDialog, odooExceptionTitleMap} from "@web/core/errors/error_dialogs";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";

odooExceptionTitleMap
    .set("odoo.addons.http_client.exceptions.AuthError", _t("Auth Error"))
    .set("odoo.addons.http_client.exceptions.AuthDataError", _t("Auth Data Error"));

registry
    .category("error_dialogs")
    .add("odoo.addons.http_client.exceptions.AuthError", WarningDialog)
    .add("odoo.addons.http_client.exceptions.AuthDataError", WarningDialog);
