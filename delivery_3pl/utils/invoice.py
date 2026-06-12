def invoice_3pl_order(sale_order):
    env = sale_order.env
    invoices = sale_order._create_invoices()
    tpl_service = sale_order.tpl_service_id
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


def send_invoice_email(inv):
    env = inv.env
    wizard = (
        env['account.move.send.wizard']
        # .with_context(**ctx)
        .create(
            {
                'move_id': inv.id,
            }
        )
    )
    return wizard.action_send_and_print()


def send_invoices(invoices):
    for inv in invoices:
        send_invoice_email(inv)
