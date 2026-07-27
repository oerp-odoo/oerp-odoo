from __future__ import annotations

from odoo.fields import Command

from ..pydantic_models.orm import OrmFieldSpec, OrmModel
from . import common


class TestPydanticOrmSerializer(common.TestApiBaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.PydanticOrmSerializer = cls.env['pydantic.orm.serializer']
        cls.partner_1 = cls.ResPartner.create(
            {
                'name': 'MY-PARTNER-1',
                'is_company': True,
            }
        )

    def test_01_serialize_impicit_all_match(self):
        # GIVEN
        class PartnerResponse(OrmModel):
            name: str
            is_company: bool

        pr = PartnerResponse(name="MY-PARTNER-1", is_company=True)
        # WHEN
        res = self.PydanticOrmSerializer.serialize(pr, self.ResPartner)
        # THEN
        self.assertEqual(
            res,
            {
                'name': 'MY-PARTNER-1',
                'is_company': True,
            },
        )

    def test_02_serialize_wih_optional_not_set(self):
        # GIVEN
        class PartnerResponse(OrmModel):
            email: str | None = None

        pr = PartnerResponse()
        # WHEN
        res = self.PydanticOrmSerializer.serialize(pr, self.ResPartner)
        # THEN
        self.assertEqual(res, {})

    def test_03_deserialize_wih_optional_set(self):
        # GIVEN
        class PartnerResponse(OrmModel):
            email: str | None = None

        pr = PartnerResponse(email='my@example.com')
        # WHEN
        res = self.PydanticOrmSerializer.serialize(pr, self.ResPartner)
        # THEN
        self.assertEqual(res, {'email': 'my@example.com'})

    def test_04_serialize_with_map(self):
        # GIVEN
        class PartnerResponse(OrmModel):
            name: str
            my_is_company: bool

            @classmethod
            def get_orm_map(cls):
                return {'my_is_company': OrmFieldSpec(odoo_field='is_company')}

        pr = PartnerResponse(name='MY-PARTNER-1', my_is_company=True)
        # WHEN
        res = self.PydanticOrmSerializer.serialize(pr, self.ResPartner)
        # THEN
        self.assertEqual(res, {'name': 'MY-PARTNER-1', 'is_company': True})

    def test_05_serialize_with_custom_converter(self):
        # GIVEN
        class PartnerResponse(OrmModel):
            name: str

            @classmethod
            def get_orm_map(cls):
                return {
                    'name': OrmFieldSpec(
                        odoo_field='name', converter=lambda pm, v, om: v.lower()
                    )
                }

        pr = PartnerResponse(name='MY-PARTNER-1')

        # WHEN
        res = self.PydanticOrmSerializer.serialize(pr, self.ResPartner)
        # THEN
        self.assertEqual(res, {'name': 'my-partner-1'})

    def test_06_serialize_with_m2o(self):
        # GIVEN
        class PartnerResponse(OrmModel):
            name: str
            parent: PartnerResponse | None = None

            @classmethod
            def get_orm_map(cls) -> dict:
                return {
                    'parent': OrmFieldSpec(
                        odoo_field='parent_id',
                    )
                }

        parent_pr = PartnerResponse(name='MY-PARTNER-1')
        child_pr = PartnerResponse(name='MY-CHILD-PARTNER-1', parent=parent_pr)
        # WHEN
        res = self.PydanticOrmSerializer.serialize(child_pr, self.ResPartner)
        # THEN
        self.assertEqual(
            res, {'name': 'MY-CHILD-PARTNER-1', 'parent_id': {'name': 'MY-PARTNER-1'}}
        )

    def test_07_serialize_with_m2o_and_converter(self):
        # GIVEN
        class PartnerResponse(OrmModel):
            name: str
            parent: PartnerResponse | None = None

            @classmethod
            def get_orm_map(cls) -> dict:
                return {
                    'parent': OrmFieldSpec(
                        odoo_field='parent_id',
                        converter=lambda pm, v, om: om.parent_id.id,
                    )
                }

        parent_pr = PartnerResponse(name='MY-PARTNER-1')
        child_pr = PartnerResponse(name='MY-CHILD-PARTNER-1', parent=parent_pr)
        child_partner = self.ResPartner.create(
            {'name': 'MY-CHILD-PARTNER-1', 'parent_id': self.partner_1.id}
        )
        # WHEN
        res = self.PydanticOrmSerializer.serialize(child_pr, child_partner)
        # THEN
        self.assertEqual(
            res, {'name': 'MY-CHILD-PARTNER-1', 'parent_id': self.partner_1.id}
        )

    def test_08_serialize_with_o2m(self):
        # GIVEN
        class PartnerResponse(OrmModel):
            name: str
            childs: list[PartnerResponse] | None = None

            @classmethod
            def get_orm_map(cls) -> dict:
                return {
                    'childs': OrmFieldSpec(
                        odoo_field='child_ids',
                        converter=lambda pm, v, om: Command.create(v),
                    )
                }

        child_pr = PartnerResponse(
            name='MY-CHILD-PARTNER-1',
        )
        parent_pr = PartnerResponse(name='MY-PARTNER-1', childs=[child_pr])
        # WHEN
        res = self.PydanticOrmSerializer.serialize(parent_pr, self.ResPartner)
        # THEN
        self.assertEqual(
            res,
            {
                'name': 'MY-PARTNER-1',
                'child_ids': [Command.create({'name': 'MY-CHILD-PARTNER-1'})],
            },
        )
