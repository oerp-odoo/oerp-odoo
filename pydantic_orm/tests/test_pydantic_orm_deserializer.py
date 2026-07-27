from __future__ import annotations

from ..pydantic_models.orm import OrmFieldSpec, OrmModel
from . import common


class TestPydanticOrmDeserializer(common.TestApiBaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.PydanticOrmDeserializer = cls.env['pydantic.orm.deserializer']
        cls.partner_1 = cls.ResPartner.create(
            {
                'name': 'MY-PARTNER-1',
                'is_company': True,
            }
        )

    def test_01_deserialize_impicit_all_match(self):
        # GIVEN
        class PartnerResponse(OrmModel):
            name: str
            is_company: bool

        # WHEN
        res = self.PydanticOrmDeserializer.deserialize(self.partner_1, PartnerResponse)
        # THEN
        self.assertEqual(res, PartnerResponse(name='MY-PARTNER-1', is_company=True))

    def test_02_deserialize_wih_optional_not_set(self):
        # GIVEN
        class PartnerResponse(OrmModel):
            email: str | None = None

        # WHEN
        res = self.PydanticOrmDeserializer.deserialize(self.partner_1, PartnerResponse)
        # THEN
        self.assertEqual(res, PartnerResponse())

    def test_03_deserialize_wih_optional_set(self):
        # GIVEN
        self.partner_1.email = 'my@example.com'

        class PartnerResponse(OrmModel):
            email: str | None = None

        # WHEN
        res = self.PydanticOrmDeserializer.deserialize(self.partner_1, PartnerResponse)
        # THEN
        self.assertEqual(res, PartnerResponse(email='my@example.com'))

    def test_04_deserialize_with_map(self):
        # GIVEN
        class PartnerResponse(OrmModel):
            name: str
            my_is_company: bool

            @classmethod
            def get_orm_map(cls):
                return {'my_is_company': OrmFieldSpec(odoo_field='is_company')}

        # WHEN
        res = self.PydanticOrmDeserializer.deserialize(self.partner_1, PartnerResponse)
        # THEN
        self.assertEqual(res, PartnerResponse(name='MY-PARTNER-1', my_is_company=True))

    def test_05_deserialize_with_custom_converter(self):
        # GIVEN
        class PartnerResponse(OrmModel):
            name: str

            @classmethod
            def get_orm_map(cls):
                return {
                    'name': OrmFieldSpec(
                        odoo_field='name', converter=lambda rec, v, pm: v.lower()
                    )
                }

        # WHEN
        res = self.PydanticOrmDeserializer.deserialize(self.partner_1, PartnerResponse)
        # THEN
        self.assertEqual(res, PartnerResponse(name='my-partner-1'))

    def test_06_deserialize_with_m2o(self):
        # GIVEN
        class PartnerResponse(OrmModel):
            name: str
            parent: PartnerResponse | None = None

            @classmethod
            def get_orm_map(cls) -> dict:
                return {
                    'parent': OrmFieldSpec(
                        odoo_field='parent_id',
                        submodel=cls,
                    )
                }

        child_partner = self.ResPartner.create(
            {'name': 'MY-CHILD-PARTNER-1', 'parent_id': self.partner_1.id}
        )
        # WHEN
        res = self.PydanticOrmDeserializer.deserialize(child_partner, PartnerResponse)
        # THEN
        self.assertEqual(
            res,
            PartnerResponse(
                name='MY-CHILD-PARTNER-1', parent=PartnerResponse(name='MY-PARTNER-1')
            ),
        )

    def test_07_deserialize_with_o2m(self):
        # GIVEN
        class PartnerResponse(OrmModel):
            name: str
            childs: list[PartnerResponse] | None = None

            @classmethod
            def get_orm_map(cls) -> dict:
                return {
                    'childs': OrmFieldSpec(
                        odoo_field='child_ids',
                        submodel=cls,
                    )
                }

        self.ResPartner.create(
            {'name': 'MY-CHILD-PARTNER-1', 'parent_id': self.partner_1.id}
        )
        # WHEN
        res = self.PydanticOrmDeserializer.deserialize(self.partner_1, PartnerResponse)
        # THEN
        self.assertEqual(
            res,
            PartnerResponse(
                name='MY-PARTNER-1', childs=[PartnerResponse(name='MY-CHILD-PARTNER-1')]
            ),
        )
