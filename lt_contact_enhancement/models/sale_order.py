##############################################################################
# Copyright (c) 2022 lumitec GmbH (https://www.lumitec.solutions)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
from odoo import models


class SalesLastOrderDate(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        """ Update last order date in contacts """
        res = super(SalesLastOrderDate, self).action_confirm()
        self.partner_id.last_order_date = self.date_order
        return res

    def action_cancel(self):
        """ Update last order date when cancel a sale order"""
        res = super(SalesLastOrderDate, self).action_cancel()
        last_order = self.env['sale.order'].search([
            ('partner_id', '=', self.partner_id.id), ('state', '=', 'sale')],
            order='date_order desc', limit=1)
        if last_order:
            self.partner_id.last_order_date = last_order.date_order
        else:
            self.partner_id.last_order_date = False
        return res
