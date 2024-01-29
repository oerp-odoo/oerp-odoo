from .common import TestProductStampConfiguratorCommon


class TestPricelistTracking(TestProductStampConfiguratorCommon):
    def test_01_track_deleted_pricelist_item(self):
        # GIVEN
        item = self.stamp_pricelist_deco.item_ids[0]
        msg = f'<br>* name: {item.display_name}, price: {item.price}<br>'
        # WHEN
        item.unlink()
        # THEN
        message = self.stamp_pricelist_deco.message_ids[0]
        self.assertIn(f'Items were deleted:{msg}', message.body)
