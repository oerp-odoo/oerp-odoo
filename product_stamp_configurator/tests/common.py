from odoo.tests.common import TransactionCase


class TestProductStampConfiguratorCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductProduct = cls.env['product.product']
        cls.StampConfigure = cls.env['stamp.configure']
        cls.StampDesign = cls.env['stamp.design']
        cls.StampDie = cls.env['stamp.die']
        cls.StampPricelist = cls.env['stamp.pricelist']
        cls.StampDifficulty = cls.env['stamp.difficulty']
        cls.StampFinishing = cls.env['stamp.finishing']
        cls.StampMaterial = cls.env['stamp.material']
        cls.partner_deco = cls.env.ref('base.res_partner_2')
        cls.partner_azure = cls.env.ref('base.res_partner_12')
        cls.company_main = cls.env.ref('base.main_company')
        cls.product_categ_consu = cls.env.ref('product.product_category_consumable')
        cls.product_categ_furniture = cls.env.ref('product.product_category_5')
        cls.product_categ_service = cls.env.ref('product.product_category_3')
        cls.product_categ_consu.stamp_type = 'die'
        cls.product_categ_furniture.stamp_type = 'counter_die'
        cls.product_categ_service.stamp_type = 'mold'
        cls.product_bin = cls.env.ref('product.product_product_9')
        cls.product_drawer = cls.env.ref('product.product_product_27')
        cls.company_main.write(
            {
                'category_default_counter_die_id': cls.product_categ_furniture.id,
                'category_default_mold_id': cls.product_categ_service.id,
            }
        )
        cls.stamp_design_f = cls.StampDesign.create(
            {
                'name': 'HFS',
                'code': 'F',
                'category_id': cls.product_categ_consu.id,
                'engraving_speed': 25,
                'weight_coefficient': 1.4,
                'company_id': cls.company_main.id,
            }
        )
        cls.stamp_design_fe = cls.StampDesign.create(
            {
                'name': 'Foil + Emboss',
                'code': 'FE',
                'is_embossed': True,
                'design_base_embossed_id': cls.stamp_design_f.id,
                'category_id': cls.product_categ_consu.id,
                'engraving_speed': 70,
                'weight_coefficient': 1.2,
                'company_id': cls.company_main.id,
            }
        )
        cls.stamp_die_default = cls.StampDie.create(
            {'name': 'Die', 'company_id': cls.company_main.id}
        )
        cls.stamp_die_insert = cls.StampDie.create(
            {'name': 'Insert Die', 'code': 'i', 'company_id': cls.company_main.id}
        )
        cls.stamp_difficulty_a = cls.StampDifficulty.create(
            {
                'name': 'A',
                'coefficient': 0.75,
                'company_id': cls.company_main.id,
            }
        )
        cls.stamp_finishing_nickel = cls.StampFinishing.create(
            {
                'name': 'Nickel coating',
                'price': 0.16,
                'code': 'N',
                'company_id': cls.company_main.id,
            }
        )
        cls.stamp_material_brass_7 = cls.StampMaterial.create(
            {
                'name': 'Brass 7',
                'code': 'B7',
                'label': 'Brass',
                'thickness': 7,
                'product_id': cls.product_bin.id,
                'price': 0.09,
                'weight_coefficient': 1.4,
                'company_id': cls.company_main.id,
            }
        )
        cls.stamp_material_plastic_05 = cls.StampMaterial.create(
            {
                'name': 'Plastic 0.5',
                'code': 'P0.5',
                'label': 'Plastic',
                'thickness': 0.5,
                'product_id': cls.product_drawer.id,
                'price': 0.02,
                'weight_coefficient': 0.6,
                'company_id': cls.company_main.id,
            }
        )
        # Stamp pricelists
        cls.stamp_pricelist_deco, cls.stamp_pricelist_azure = cls.StampPricelist.create(
            [
                {
                    'name': 'Pricelist 1',
                    'price_counter_die': 0.09,
                    'mold_of_die_perc': 100.0,
                    'quantity_die_mold_free': 5.0,
                    'company_id': cls.company_main.id,
                    'item_ids': [
                        (0, 0, {'design_id': cls.stamp_design_f.id, 'price': 0.25}),
                        (0, 0, {'design_id': cls.stamp_design_fe.id, 'price': 0.25}),
                    ],
                },
                {
                    'name': 'Pricelist 2',
                    'price_counter_die': 0.08,
                    'mold_of_die_perc': 50.0,
                    'quantity_die_mold_free': 10.0,
                    'company_id': cls.company_main.id,
                    'item_ids': [
                        (0, 0, {'design_id': cls.stamp_design_f.id, 'price': 0.17}),
                        (0, 0, {'design_id': cls.stamp_design_fe.id, 'price': 0.23}),
                    ],
                },
            ]
        )
        cls.partner_deco.property_stamp_pricelist_id = cls.stamp_pricelist_deco.id
        cls.partner_azure.property_stamp_pricelist_id = cls.stamp_pricelist_azure.id
