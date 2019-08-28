odoo.define('website_snippet_code.code_highlight', function () {
"use strict";
/*global hljs */

    var CLASS_CODE_RAW = 'o_website_snippet_code_raw',
        CLASS_CODE_HIGHLIGHT = 'o_website_snippet_code_highlight',
        PRE_CODE_RAW = 'pre.' + CLASS_CODE_RAW,
        PRE_CODE_HIGHLIGHT = 'pre.' + CLASS_CODE_HIGHLIGHT,
        IGNORED_CLASSES =['auto'];

    function getSupportedClasses(){
        return hljs.listLanguages().concat(['nohighlight'])
    }

    function getClassForHighlight(used_classes){
        var no_class = ''
        for (var i = 0; i < used_classes.length; i++) {
            var used_class = used_classes[i];
            if (IGNORED_CLASSES.indexOf(used_class) != -1){
                return no_class
            }
            var supported_classes = getSupportedClasses()
            var matched_class_idx = supported_classes.indexOf(used_class)
            if (matched_class_idx != -1){
                return supported_classes[matched_class_idx]
            }
        }
        return no_class
    }

    function copyItems(items_to_copy, exclude){
        var items = [],
            item;
        for (var i = 0; i < items_to_copy.length; i++) {
            item = items_to_copy[i];
            if(exclude.indexOf(item) == -1){
                items.push(item)
            }
        }
        return items;
    }

    function getClassesForHighlight(pre_raw, used_classes){
        var classes = [CLASS_CODE_HIGHLIGHT],
            highlight_class = getClassForHighlight(used_classes);
        if (highlight_class){
            classes.push(highlight_class);
        }
        // Copy classes from raw pre element to keep expected style (
        // e.g. using bootstrap classes to split into columns)
        var pre_raw_classes = copyItems(pre_raw.classList, [CLASS_CODE_RAW]);
        return classes.concat(pre_raw_classes);
    }

    function getHtmlForHighlight(pre_raw, used_classes){
        var classes = getClassesForHighlight(pre_raw, used_classes)
        // Split into two template strings for more convenient
        // line break (that allows for indentation).
        return `<pre class="${classes.join(' ')}">`+
        `<code>${pre_raw.innerHTML}</code></pre>`;

    }

    function createElementForHighlight(pre_raw, used_classes){
        return $(getHtmlForHighlight(pre_raw, used_classes))
    }

    function replaceBrWithNewLine(str){
        return str.replace(/<br[^>]*>/gi, '\n')
    }

    function highlight($pre_raw, $pre_hl){
        // Replace br with \n, because br element is incorrectly
        // interpreted when highlighting.
        var html_str_to_hl = replaceBrWithNewLine($pre_hl.html());
        $pre_hl.html(html_str_to_hl);
        $pre_raw.hide();
        $pre_hl.insertAfter($pre_raw[0]);
        hljs.highlightBlock($pre_hl[0]);
    }
    $(document).ready(function() {
        var snippets = $('.o_website_snippet_code');
        snippets.each(function(i, snippet){
            var $snippet = $(snippet);
            // Highlight code only if its not edited.
            if (!$snippet.parent().hasClass('o_editable')){
                // Remove old highlighted blocks.
                $snippet.find(PRE_CODE_HIGHLIGHT).remove();
                // There can be more than one `pre` element per snippet
                // if snippet is split in more than one column.
                $snippet.find(PRE_CODE_RAW).each(function(i, pre) {
                    var $pre_hl = createElementForHighlight(
                        pre, snippet.classList);
                    highlight($(pre), $pre_hl);
                })
            }
        })
    });
    return {
        CLASS_CODE_RAW: CLASS_CODE_RAW,
        CLASS_CODE_HIGHLIGHT: CLASS_CODE_HIGHLIGHT,
        PRE_CODE_RAW: PRE_CODE_RAW,
        PRE_CODE_HIGHLIGHT: PRE_CODE_HIGHLIGHT,
        functions: {
            getSupportedClasses: getSupportedClasses,
            getClassForHighlight: getClassForHighlight,
            copyItems: copyItems,
            getClassesForHighlight: getClassesForHighlight,
            getHtmlForHighlight: getHtmlForHighlight,
            createElementForHighlight: createElementForHighlight,
            replaceBrWithNewLine: replaceBrWithNewLine,
            highlight: highlight,
        }
    }
});

