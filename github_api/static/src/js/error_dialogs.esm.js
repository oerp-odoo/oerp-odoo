/** @odoo-module */

import {WarningDialog, odooExceptionTitleMap} from "@web/core/errors/error_dialogs";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";

odooExceptionTitleMap.set(
    "odoo.addons.github_api.exceptions.MissingGithubError",
    _t("Missing Github Error")
);

registry
    .category("error_dialogs")
    .add("odoo.addons.github_api.exceptions.MissingGithubError", WarningDialog);
