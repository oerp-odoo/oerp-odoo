from odoo import models


class StockChainAutoDone(models.AbstractModel):
    _name = 'stock.chain.auto.done'
    _description = "Stock Chain Auto Done Service"

    def handle_chain_done(self, picking):
        pickings_next = self._get_next_pickings_to_done(picking)
        if not pickings_next:
            return self.env['stock.picking']
        pickings_next.button_validate()
        return pickings_next

    def _get_next_pickings_to_done(self, picking):
        chain_locations = self.env['stock.chain.rule'].get_locations(
            picking.company_id.id
        )
        if not chain_locations:
            return self.env['stock.picking']
        pickings = self.env['stock.picking']
        for move in picking.move_ids:
            pickings |= self._match_chained_pickings_by_location(
                move, move.move_dest_ids, chain_locations
            )
        return pickings

    def _match_chained_pickings_by_location(
        self, src_move, dest_moves, chain_locations
    ):
        matched_pickings = not_matched_pickings = self.env['stock.picking']
        for dest_move in dest_moves:
            next_picking = dest_move.picking_id
            # Picking must be ready to be auto done.
            if next_picking.state != 'assigned':
                continue
            if self._predicate_chained_move_location(
                src_move, dest_move, chain_locations
            ):
                matched_pickings |= next_picking
            else:
                not_matched_pickings |= next_picking
        return matched_pickings - not_matched_pickings

    def _predicate_chained_move_location(self, src_move, dest_move, chain_locations):
        if src_move.location_dest_id != dest_move.location_id:
            return False
        return src_move.location_dest_id in chain_locations
