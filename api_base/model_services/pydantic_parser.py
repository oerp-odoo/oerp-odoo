import pydantic

from odoo import fields, models

from ..pydantic_models.field import FieldOrm


def set_val(vals: dict, val: any, fname: str, to_extend=False):
    if val is not None:
        # With x2m commands we want to extend if multiple
        # commands are used for same field!
        if to_extend and fname in vals:
            vals[fname].extend(val)
        else:
            vals[fname] = val


class PydanticParser(models.AbstractModel):
    """Base class to parse pydantic model to odoo data.

    Pydantic model is parsed into dictionary that is compatible to
    target odoo model (to have create or write operations).
    """

    _name = 'pydantic.parser'
    _description = "Pydantic Parser"

    def parse(self, obj: pydantic.BaseModel):
        """Parse pydantic model into odoo model vals dictionary."""
        vals = {}
        used_keys = set()
        # 1. Parse map.
        for src_fname, field_orm in self.get_orm_map():
            used_keys.add(src_fname)
            val_ = self._parse_value(obj, src_fname, field_orm)
            set_val(vals, val_, field_orm.fname, to_extend=field_orm.x2m is not None)
        # 2. Parse direct mapped fields.
        # NOTE. All left fields that were not mapped explicitly are
        # assumed that have exact mapping with odoo fields and without
        # any conversion!
        for fname in self._get_direct_map_fields(obj, used_keys):
            set_val(vals, self._get_obj_value(obj, fname), fname)
        return vals

    def get_orm_map(self) -> list[tuple[str, FieldOrm]]:
        """Return mapping to convert pydantic model to odoo data.

        Extend to specify field mappings.

        Not specified fields are assumed either directly mapped (same
        key) or having custom getter.
        """
        return []

    def _get_direct_map_fields(self, obj: pydantic.BaseModel, used_keys: set):
        keys = []
        # NOTE. We must use pydantic.BaseModel instance here and not class itself,
        # to make sure changes from extensions are taken in consideration.
        # Because it only works for instances of a class, not class itself!
        all_keys = obj.__fields__.keys()
        for key in all_keys:
            if key not in used_keys:
                keys.append(key)
        return keys

    def _parse_value(
        self, obj: pydantic.BaseModel, src_fname: str, field_orm: FieldOrm
    ):
        def parse(val, subparser: str, converter):
            if subparser is not None:
                val = self.env[subparser].parse(val)
            if converter is not None:
                val = converter(self.env, val)
            return val

        val = self._get_obj_value(obj, src_fname)
        if val is not None:
            subparser = field_orm.subparser
            converter = field_orm.converter
            x2m = field_orm.x2m
            if x2m is None:
                val = parse(val, subparser, converter)
            else:
                data = []
                vals_list = val if x2m.src_iterated else [val]
                for val_ in vals_list:
                    cmd_val = parse(val_, subparser, converter)
                    if cmd_val is None:
                        continue
                    data.append(self._prepare_x2m_cmd(x2m.cmd, cmd_val))
                if not data:
                    return None
                return data
        return val

    def _get_obj_value(self, obj: pydantic.BaseModel, fname: str):
        return getattr(obj, fname)

    def _prepare_x2m_cmd(self, cmd: fields.Command, val: any):
        if cmd.value == 0:
            return cmd.create(val)
        if cmd.value == 1:
            # val must be tuple
            return cmd.update(val[0], val[1])
        if cmd.value == 2:
            return cmd.delete(val)
        if cmd.value == 3:
            return cmd.unlink(val)
        if cmd.value == 4:
            return cmd.link(val)
        if cmd.value == 5:
            return cmd.clear()
        if cmd.value == 6:
            # val must be list of ids
            return cmd.set(val)
