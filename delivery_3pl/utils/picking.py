import logging

from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


def force_picking_done(picking):
    picking.move_ids.mapped('move_line_ids').write({'picked': True})
    _auto_assign_missing(picking)
    # Passing context to make sure email is sent only if picking is in
    # done state!
    picking.with_context(stock_move_email_on_done=True)._action_done()


def auto_finish_picking(picking, raise_exc=True):
    """Reserve and make picking done if all needed quantity is reserved."""
    try:
        picking.action_assign()
        # picking.action_set_quantities_to_reservation()
        # Passing context to make sure email is sent only if picking is in
        # done state!
        picking.with_context(stock_move_email_on_done=True).button_validate()
    except (UserError, ValidationError) as e:
        if raise_exc:
            raise
        _logger.info("Picking not auto finished. Got Exception: %s", str(e))
    return True


# TODO: implement option to either force assign or rely on available
# reservation only.
def _auto_assign_missing(picking):
    # NOTE. Currently we force assign all missing, except serial/lots.
    moves = picking.move_ids
    moves_todo_map = {m.id: m.product_uom_qty for m in moves}
    # Deduct already done quantities.
    for move in moves:
        # TODO: implement handling of serial/lot.
        for ml in move.move_line_ids:
            moves_todo_map[move.id] -= ml.quantity
    data = []
    for move_id, qty_done in moves_todo_map.items():
        if qty_done <= 0:
            continue
        move = moves.browse(move_id)
        data.append(
            (
                0,
                0,
                {
                    'product_id': move.product_id.id,
                    'product_uom_id': move.product_uom.id,
                    'move_id': move.id,
                    'location_id': move.location_id.id,
                    'location_dest_id': move.location_dest_id.id,
                    'quantity': qty_done,
                    'picked': True,
                },
            )
        )
    if data:
        picking.move_line_ids = data
