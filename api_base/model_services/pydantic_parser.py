import pydantic

from odoo import fields, models

from ..pydantic_models.field import FieldOrm


class PydanticParser(models.AbstractModel):
    """Base class to parse pydantic model to odoo data.

    Pydantic model is parsed into dictionary that is compatible to
    target odoo model (to have create or write operations).
    """

    _name = 'pydantic.parser'
    _description = "Pydantic Parser"

    def parse(self, obj: pydantic.BaseModel):
        """Parse pydantic model into odoo model vals dictionary."""

        def set_val(vals: dict, val: any, dest_fname: str):
            if val is not None:
                vals[dest_fname] = val

        vals = {}
        used_keys = []
        # 1. Parse map.
        for src_fname, field_orm in self.get_orm_map().items():
            used_keys.append(src_fname)
            set_val(vals, self._parse_value(obj, src_fname, field_orm), field_orm.fname)
        # 2. Parse direct mapped fields.
        # NOTE. All left fields that were not mapped explicitly are
        # assumed that have exact mapping with odoo fields and without
        # any conversion!
        for fname in self._get_direct_map_fields(obj, used_keys):
            set_val(vals, self._get_obj_value(obj, fname), fname)
        return vals

    def get_orm_map(self) -> dict[str, FieldOrm]:
        """Return mapping to convert pydantic model to odoo data.

        Override to specify field mappings.

        Not specified fields are assumed either directly mapped (same
        key) or having custom getter.
        """
        return {}

    def _get_direct_map_fields(self, obj: pydantic.BaseModel, used_keys: list):
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
            x2m_cmd = field_orm.x2m_cmd
            if x2m_cmd is None:
                val = parse(val, subparser, converter)
            else:
                data = []
                # `val` is expected to be sequence to iterate over.
                for val_ in val:
                    data.append(
                        self._prepare_x2m_cmd(
                            x2m_cmd, parse(val_, subparser, converter)
                        )
                    )
                return data
        return val

    def _get_obj_value(self, obj: pydantic.BaseModel, fname: str):
        return getattr(obj, fname)

    def _prepare_x2m_cmd(self, x2m_cmd: fields.Command, val: any):
        if x2m_cmd.value == 0:
            return x2m_cmd.create(val)
        if x2m_cmd.value == 1:
            # val must be tuple
            return x2m_cmd.update(val[0], val[1])
        if x2m_cmd.value == 2:
            return x2m_cmd.delete(val)
        if x2m_cmd.value == 3:
            return x2m_cmd.unlink(val)
        if x2m_cmd.value == 4:
            return x2m_cmd.link(val)
        if x2m_cmd.value == 5:
            return x2m_cmd.clear()
        if x2m_cmd.value == 6:
            # val must be list of ids
            return x2m_cmd.set(val)
