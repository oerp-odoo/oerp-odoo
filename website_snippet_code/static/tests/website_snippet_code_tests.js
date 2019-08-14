odoo.define('website_snippet_code.tests', function (require) {
"use strict";
/*global QUnit*/

var CodeHighlight = require('website_snippet_code.code_highlight');

QUnit.module('website_snippet_code', {
    before: function () {
        var functions = CodeHighlight['functions'];
        this.supported_classes = functions.getSupportedClasses();
        this.getClassForHighlight = functions.getClassForHighlight;
        this.copyItems = functions.copyItems;
        this.createElementForHighlight = functions.createElementForHighlight;
        this.highlight = functions.highlight;
        this.pre_raw_outer_html = `<pre class="`+`
        ${CodeHighlight['CLASS_CODE_RAW']}">def test():
    pass</pre>`
    }
});

QUnit.test("Supported classes: found", function (assert) {
    assert.expect(3);
    assert.notStrictEqual(this.supported_classes.indexOf('python'), -1);
    assert.notStrictEqual(this.supported_classes.indexOf('plaintext'), -1);
    assert.notStrictEqual(this.supported_classes.indexOf(
        'nohighlight'), -1);
});
QUnit.test("Supported classes: not found", function (assert) {
    assert.expect(1);
    assert.strictEqual(this.supported_classes.indexOf(
        'not_existing_class_123'), -1);
});

QUnit.test("Class for highlight: no_class", function (assert) {
    assert.expect(3);
    assert.strictEqual(this.getClassForHighlight(['a', 'b']), '');
    assert.strictEqual(this.getClassForHighlight(['auto']), '');
    // auto is found first, so it should default to that.
    assert.strictEqual(this.getClassForHighlight(['auto', 'python']), '');
});
QUnit.test("Class for highlight: python", function (assert) {
    assert.expect(3);
    assert.strictEqual(this.getClassForHighlight(['a', 'python']), 'python');
    assert.strictEqual(this.getClassForHighlight(
        ['python', 'auto']), 'python');
    assert.strictEqual(this.getClassForHighlight(
        ['python', 'plaintext']), 'python');
});
QUnit.test("Class for highlight: plaintext", function (assert) {
    assert.expect(3);
    assert.strictEqual(this.getClassForHighlight(
        ['a', 'plaintext']), 'plaintext');
    assert.strictEqual(this.getClassForHighlight(
        ['plaintext', 'auto']), 'plaintext');
    assert.strictEqual(this.getClassForHighlight(
        ['plaintext', 'python']), 'plaintext');
});
QUnit.test("Class for highlight: nohighlight", function (assert) {
    assert.expect(3);
    assert.strictEqual(this.getClassForHighlight(
        ['a', 'nohighlight']), 'nohighlight');
    assert.strictEqual(this.getClassForHighlight(
        ['nohighlight', 'auto']), 'nohighlight');
    assert.strictEqual(this.getClassForHighlight(
        ['nohighlight', 'python']), 'nohighlight');
});

QUnit.test("Copy items: no exclusion", function (assert) {
    assert.expect(1);
    assert.deepEqual(
        this.copyItems(['a', 'b'], []), ['a', 'b']);
});
QUnit.test("Copy items: partial exclusion", function (assert) {
    assert.expect(3);
    assert.deepEqual(
        this.copyItems(['a', 'b'], ['b']), ['a']);
    assert.deepEqual(
        this.copyItems(['a', 'b', 'c'], ['b', 'c']), ['a']);
    assert.deepEqual(
        this.copyItems(['a', 'b', 'c'], ['b']), ['a', 'c']);
});
QUnit.test("Copy items: full exclusion", function (assert) {
    assert.expect(2);
    assert.deepEqual(
        this.copyItems(['a', 'b'], ['a', 'b']), []);
    assert.deepEqual(
        this.copyItems(['a', 'b', 'c'], ['a', 'b', 'c']), []);
});

QUnit.test("createElementForHighlight: extra class copied", function (assert) {
    assert.expect(2);
    var $pre_raw = $(this.pre_raw_outer_html);
    // Add custom class on pre_raw element, so it would be copied
    // on pre_hl element.
    $pre_raw.addClass('custom_cls')
    var $pre_hl = this.createElementForHighlight($pre_raw[0], []);
    assert.ok($pre_hl.hasClass(CodeHighlight['CLASS_CODE_HIGHLIGHT']))
    assert.ok($pre_hl.hasClass('custom_cls'))
});

QUnit.test("highlight: automatic language detection", function (assert) {
    assert.expect(5);
    var $pre_raw = $(this.pre_raw_outer_html),
        $pre_hl = this.createElementForHighlight($pre_raw[0], []);
    assert.ok($pre_hl.hasClass(CodeHighlight['CLASS_CODE_HIGHLIGHT']))
    this.highlight($pre_raw, $pre_hl)
    assert.strictEqual($pre_raw.css('display'), 'none')
    // is(':visible') won't work here, because it also checks for parent
    // visibility, but we need to check specifically for this element
    // only.
    assert.strictEqual($pre_hl.css('display'), '')
    assert.ok($pre_hl.hasClass('hljs'))
    assert.ok($pre_hl.hasClass('python'))
});
QUnit.test("highlight: custom language selected", function (assert) {
    assert.expect(7);
    var $pre_raw = $(this.pre_raw_outer_html),
        $pre_hl = this.createElementForHighlight($pre_raw[0], ['javascript']);
    assert.ok($pre_hl.hasClass(CodeHighlight['CLASS_CODE_HIGHLIGHT']))
    assert.ok($pre_hl.hasClass('javascript'))
    this.highlight($pre_raw, $pre_hl)
    assert.strictEqual($pre_raw.css('display'), 'none')
    assert.strictEqual($pre_hl.css('display'), '')
    assert.ok($pre_hl.hasClass('hljs'))
    assert.ok($pre_hl.hasClass('javascript'))
    assert.notOk($pre_hl.hasClass('python'))
});

});
