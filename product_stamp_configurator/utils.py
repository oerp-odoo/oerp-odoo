from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FieldTranslation:
    fname: str
    # Record to do translations on.
    record: any
    langs: tuple[str]
    func: callable
    # Must be record, to be able to pass context.
    first_func_arg: any
    func_args: tuple = ()
    func_kwargs: dict | None = None


def translate_field(field_translation: FieldTranslation):
    fname = field_translation.fname
    func_kwargs = field_translation.func_kwargs
    if func_kwargs is None:
        func_kwargs = {}
    translations = {}
    for lang in field_translation.langs:
        func = field_translation.func
        first_arg = field_translation.first_func_arg
        val = func(
            first_arg.with_context(lang=lang),
            *field_translation.func_args,
            **func_kwargs,
        )
        translations[lang] = val
    field_translation.record.update_field_translations(fname, translations)
