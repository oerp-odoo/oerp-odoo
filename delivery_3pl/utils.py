from urllib.parse import urljoin


def invoice_3pl_order(sale_order, tpl_service, logger=None):
    env = sale_order.env
    invoices = sale_order._create_invoices()
    pre_state = invoices.mapped(lambda r: (r.name, (r.state, r.payment_state)))
    state_target = tpl_service.invoice_state_target
    state_email = tpl_service.invoice_state_email
    if state_target in ('open', 'paid'):
        invoices.action_post()
        if state_email == 'open':
            send_invoices(invoices)
        if state_target == 'paid':
            # This wizard handles only one invoice at a time (though
            # most cases will be single invoice anyway).
            journal_id = tpl_service.journal_id.id
            APR = env['account.payment.register']
            for invoice in invoices:
                # Skip invoices if those are already paid (by some
                # other workflow logic).
                if invoice.payment_state in ('in_payment', 'paid'):
                    continue
                payment_register = APR.with_context(
                    active_ids=[invoice.id], active_model='account.move'
                ).create({'journal_id': journal_id})
                payment_register.action_create_payments()
            if state_email == 'paid':
                send_invoices(invoices)
    post_state = invoices.mapped(lambda r: (r.name, (r.state, r.payment_state)))
    tpl_service.log(
        '%s Invoices. Pre: %s. Post: %s',
        (tpl_service._description, pre_state, post_state),
        logger=logger,
    )


def send_invoice_email(inv):
    env = inv.env
    action_dct = inv.action_invoice_sent()
    ctx = dict(action_dct['context'], active_ids=inv.ids)
    wizard = (
        env['account.invoice.send']
        .with_context(**ctx)
        .create(
            {
                'is_print': False,
                'partner_ids': [(4, inv.partner_id.id)],
            }
        )
    )
    # To actually generate email body.
    wizard.onchange_template_id()
    return wizard.send_and_print_action()


def send_invoices(invoices):
    for inv in invoices:
        send_invoice_email(inv)


def force_picking_done(picking):
    for move in picking.move_lines.filtered(
        lambda m: m.state not in ['done', 'cancel']
    ):
        for move_line in move.move_line_ids:
            # Try to use reserve quantity only if quantity is not fully
            # done.
            if move_line.qty_done < move_line.product_uom_qty:
                move_line.qty_done = move_line.product_uom_qty
    _auto_assign_missing(picking)
    # Passing context to make sure email is sent only if picking is in
    # done state!
    picking.with_context(stock_move_email_on_done=True)._action_done()


def safe_urljoin(base_url, path, args=None):
    if not base_url.endswith('/'):
        base_url = f'{base_url}/'
    url = urljoin(base_url, path)
    if args:
        return url % args
    return url


# TODO: implement option to either force assign or rely on available
# reservation only.
def _auto_assign_missing(picking):
    # NOTE. Currently we force assign all missing, except serial/lots.
    moves = picking.move_lines
    moves_todo_map = {m.id: m.product_uom_qty for m in moves}
    # Deduct already done quantities.
    for move in moves:
        # TODO: implement handling of serial/lot.
        for ml in move.move_line_ids:
            moves_todo_map[move.id] -= ml.qty_done
    data = []
    for move_id, qty_done in moves_todo_map.items():
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
                    'qty_done': qty_done,
                },
            )
        )
    if data:
        picking.move_line_ids = data
