##############################################################################
# Copyright (c) 2022 lumitec GmbH (https://www.lumitec.solutions)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    top_filter = fields.Boolean("Is Invoice greater than zero",
                                compute='_compute_sale_amount', store=True)
    sale_amount = fields.Float('Invoice Total',
                               compute='_compute_sale_amount', store=True)
    last_order_date = fields.Datetime("Last Order Date",
                                      help="Last sale order date of this partner")

    @api.depends('invoice_ids')
    def _compute_sale_amount(self):
        """ Compute the sale amount of the partner """
        if not self.ids:
            return True

        user_currency_id = self.env.company.currency_id.id
        all_partners_and_children = {}
        all_partner_ids = []
        for partner in self:
            # price_total is in the company currency
            all_partners_and_children[partner] = self.with_context(
                active_test=False).search([('id', 'child_of', partner.id)]).ids
            all_partner_ids += all_partners_and_children[partner]

        price_totals = self.env['account.invoice.report'].search(
            [('partner_id', 'in', all_partner_ids),
             ('state', 'not in', ['draft', 'cancel']),
             ('move_type', 'in', ('out_invoice', 'out_refund'))])
        for partner, child_ids in all_partners_and_children.items():
            partner.sale_amount = sum(
                price.price_subtotal for price in price_totals if
                price.partner_id.id in child_ids)
            if partner.sale_amount > 0:
                partner.top_filter = True
            else:
                partner.top_filter = False

    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Override the search"""
        flag = 0
        for arg in args:
            if arg == ['top_filter', '!=', False]:
                flag = 1

        if flag == 1:
            order = 'sale_amount desc'
            limit = 10
        res = super(ResPartner, self).search(args, offset=offset, limit=limit, order=order, count=count)
        return res
