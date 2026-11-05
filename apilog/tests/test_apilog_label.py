from . import common


class TestApilogLabel(common.TestApilogCommon):
    def test_01_display_name_no_parent(self):
        """Check display name of a label without parent is its name."""
        # GIVEN
        label = self.ApilogLabel.create({'name': "AL-PARENT"})
        # WHEN
        display_name = label.display_name
        # THEN
        self.assertEqual(display_name, "AL-PARENT")

    def test_02_display_name_with_parent(self):
        """Check display name of a child label shows labels hierarchy."""
        # GIVEN
        parent = self.ApilogLabel.create({'name': "AL-PARENT"})
        # WHEN
        child = self.ApilogLabel.create({'name': "AL-CHILD", 'parent_id': parent.id})
        # THEN
        self.assertEqual(child.display_name, "AL-PARENT / AL-CHILD")

    def test_03_display_name_parent_renamed(self):
        """Check display name of a child label follows the parent rename."""
        # GIVEN
        parent = self.ApilogLabel.create({'name': "AL-PARENT"})
        child = self.ApilogLabel.create({'name': "AL-CHILD", 'parent_id': parent.id})
        # WHEN
        parent.name = "AL-PARENT-2"
        # THEN
        self.assertEqual(child.display_name, "AL-PARENT-2 / AL-CHILD")
