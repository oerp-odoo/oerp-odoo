odoo.define('website_snippet_code.editor', function (require) {
"use strict";

    var options = require('web_editor.snippets.options'),
        CodeHl = require('website_snippet_code.code_highlight');

    options.registry.snippet_code_options = options.Class.extend({
        init: function(){
            var result = this._super.apply(this, arguments),
                $target = this.$target;
            this._code_raw_el = $target.find(CodeHl['PRE_CODE_RAW']);
            this._code_hl_el = $target.find(CodeHl['PRE_CODE_HIGHLIGHT']);
            return result
        },
        start: function(){
            this._super.apply(this, arguments);
            this._code_raw_el.show();
            this._code_hl_el.hide();
        },
    })
});

