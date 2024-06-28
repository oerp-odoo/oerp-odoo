/** @odoo-module */

import {WarningDialog, odooExceptionTitleMap} from "@web/core/errors/error_dialogs";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";

odooExceptionTitleMap.set(
    "odoo.addons.http_client.exceptions.MissingSharepointError",
    _t("Missing Sharepoint Error")
);

registry
    .category("error_dialogs")
    .add("odoo.addons.http_client.exceptions.MissingSharepointError", WarningDialog);
