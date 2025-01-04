# class TestPackageComponentType(BaseCommon):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.PackageConfiguratorComponent = cls.env['package.configurator.component']

#     def test_01_get_box_component_types(self):
#         # GIVEN
#         PCC = self.PackageConfiguratorComponent.with_context(
#             package_type=const.PackageType.BOX
#         )
#         # WHEN
#         res = PCC.get_component_types()
#         # THEN
#         self.assertEqual(len(res), 6)
#         self.assertEqual(res[0].name, 'base_greyboard')
#         self.assertEqual(res[0].scope, const.SheetTypeScope.GREYBOARD)
#         self.assertEqual(res[1].name, 'lid_greyboard')
#         self.assertEqual(res[1].scope, const.SheetTypeScope.GREYBOARD)
#         self.assertEqual(res[2].name, 'base_wrappingpaper_inside')
#         self.assertEqual(res[2].scope, const.SheetTypeScope.WRAPPINGPAPER)
#         self.assertEqual(res[3].name, 'base_wrappingpaper_outside')
#         self.assertEqual(res[3].scope, const.SheetTypeScope.WRAPPINGPAPER)
#         self.assertEqual(res[4].name, 'lid_wrappingpaper_inside')
#         self.assertEqual(res[4].scope, const.SheetTypeScope.WRAPPINGPAPER)
#         self.assertEqual(res[5].name, 'lid_wrappingpaper_outside')
#         self.assertEqual(res[5].scope, const.SheetTypeScope.WRAPPINGPAPER)

#     def test_02_get_box_component_types_implicit(self):
#         # WHEN
#         res = self.PackageConfiguratorComponent.get_component_types()
#         # THEN
#         self.assertEqual(len(res), 6)
#         self.assertEqual(res[0].name, 'base_greyboard')
#         self.assertEqual(res[0].scope, const.SheetTypeScope.GREYBOARD)
#         self.assertEqual(res[1].name, 'lid_greyboard')
#         self.assertEqual(res[1].scope, const.SheetTypeScope.GREYBOARD)
#         self.assertEqual(res[2].name, 'base_wrappingpaper_inside')
#         self.assertEqual(res[2].scope, const.SheetTypeScope.WRAPPINGPAPER)
#         self.assertEqual(res[3].name, 'base_wrappingpaper_outside')
#         self.assertEqual(res[3].scope, const.SheetTypeScope.WRAPPINGPAPER)
#         self.assertEqual(res[4].name, 'lid_wrappingpaper_inside')
#         self.assertEqual(res[4].scope, const.SheetTypeScope.WRAPPINGPAPER)
#         self.assertEqual(res[5].name, 'lid_wrappingpaper_outside')
#         self.assertEqual(res[5].scope, const.SheetTypeScope.WRAPPINGPAPER)

#     def test_03_get_insert_component_types(self):
#         # GIVEN
#         PCC = self.PackageConfiguratorComponent.with_context(
#             package_type=const.PackageType.INSERT
#         )
#         # WHEN
#         res = PCC.get_component_types()
#         # THEN
#         self.assertEqual(len(res), 5)
#         self.assertEqual(res[0].name, 'base_carton')
#         self.assertEqual(res[0].scope, const.SheetTypeScope.CARTON)
#         self.assertEqual(res[1].name, 'base_wrappingpaper_inside')
#         self.assertEqual(res[1].scope, const.SheetTypeScope.WRAPPINGPAPER)
#         self.assertEqual(res[2].name, 'base_wrappingpaper_outside')
#         self.assertEqual(res[2].scope, const.SheetTypeScope.WRAPPINGPAPER)
#         self.assertEqual(res[3].name, 'lid_wrappingpaper_inside')
#         self.assertEqual(res[3].scope, const.SheetTypeScope.WRAPPINGPAPER)
#         self.assertEqual(res[4].name, 'lid_wrappingpaper_outside')
#         self.assertEqual(res[4].scope, const.SheetTypeScope.WRAPPINGPAPER)

#     def test_04_get_box_default_component(self):
#         # GIVEN
#         PCC = self.PackageConfiguratorComponent.with_context(
#             package_type=const.PackageType.BOX
#         )
#         # WHEN
#         res = PCC.get_default_component_type()
#         # THEN
#         self.assertEqual(res, 'base_greyboard')

#     def test_05_get_box_default_component_implicit(self):
#         # WHEN
#         res = self.PackageConfiguratorComponent.get_default_component_type()
#         # THEN
#         self.assertEqual(res, 'base_greyboard')

#     def test_06_get_insert_default_component(self):
#         # GIVEN
#         PCC = self.PackageConfiguratorComponent.with_context(
#             package_type=const.PackageType.INSERT
#         )
#         # WHEN
#         res = PCC.get_default_component_type()
#         # THEN
#         self.assertEqual(res, 'base_carton')
