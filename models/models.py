from odoo import api, fields, models, _
from datetime import timedelta,date,datetime
import logging

class ResPartnerBonCadeau(models.Model):
	_inherit = 'res.partner'
	
	list_BC = fields.One2many('bon.cadeau','user_id',required=True,ondelete='cascade')
	
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_gift_card = fields.Boolean(default=False, string="Est un bon cadeau")
	
class AccountJournal(models.Model):
	_inherit = 'account.journal'
	
	gift_card = fields.Boolean(default=False, string="Est un moyen de paiment bon cadeau")
	
class AccountBankStatementLine(models.Model):
	_inherit = 'account.bank.statement.line'
	gift_card_checked = fields.Boolean(default=False, string="Est vérifié")
	
class PosOrder(models.Model):
	_inherit = 'pos.order'
	
	def write(self,vals):
		logging.info("gift_card")
		if self.isChecked == False :
			if self.partner_id:
				for bonCadeau in self.partner_id.list_BC:
					if bonCadeau.ref_com.id == self.id:
						return super(PosOrder,self).write(vals)
				for line in self.lines:
					if line.product_id.product_tmpl_id.is_gift_card == True : 
						self.env['bon.cadeau'].create({
							"ref_com":self.id,
							"user_id":self.partner_id.id,
							"prix":self.amount_total,
						})
				if self.partner_id.list_BC:
					total_amount =0
					logging.info("debut")
					for statement in self.statement_ids:
						logging.info(statement.journal_id.gift_card)
						if statement.gift_card_checked == False :
							if statement.journal_id.gift_card:
								logging.info(statement.amount)
								total_amount = total_amount + statement.amount
								statement.gift_card_checked = True
					logging.info(total_amount)
					for bon in self.partner_id.list_BC:
						if bon.statut == "dispo":
							if bon.amount_left <= total_amount:
								total_amount = total_amount - bon.amount_left
								bon.amount_used = bon.prix
								bon.date_utilisation = date.today()
							else : 
								bon.amount_used = bon.amount_used + total_amount
								total_amount = 0						
		return super(PosOrder,self).write(vals)
		
class BonCadeau(models.Model):
	_name="bon.cadeau"
	
	ref_com = fields.Many2one('pos.order',String='Référence commande')
	user_id = fields.Many2one('res.partner',ondelete='cascade',invisible=True)
	prix=fields.Float(String='Valeur total du bon cadeau')
	amount_used=fields.Float(String='Valeur utilisé du bon cadeau')
	amount_left=fields.Float(String='Valeur restante du bon cadeau',compute='_compute_amount_left')
	date_utilisation=fields.Date(string='Date d\'utilisation')
	date_expiration=fields.Date(string='Date d\'expriation', compute='_compute_date_expiration',store=True)
	statut=fields.Selection([('dispo', 'Disponible'),('utilise', 'Utilisé'),('expire', 'Expiré')],default='dispo')
	warning_delta = fields.Float(string='Jours avant l\'alerte', compute='_compute_warning_delta')
	expiration_delta = fields.Float(string='Jours avant expiration', compute='_compute_expiration_delta')
	
	@api.depends('amount_used')
	def _compute_amount_left(self):
		for record in self:
			record.amount_left = record.prix - record.amount_used
	
	@api.depends('ref_com')
	def _compute_date_expiration(self):
		for record in self:
			if record.ref_com :
				str_creation = self.env['pos.order'].search([('id','=',self.ref_com.id)]).create_date
				if str_creation:
					date_creation = datetime.strptime(str_creation, '%Y-%m-%d %H:%M:%S')
					record.date_expiration = date_creation.date()+timedelta(days=122)
	
	@api.depends('ref_com')
	def _compute_warning_delta(self):
		for record in self:
			if record.date_expiration:
				today = date.today()
				expiration = datetime.strptime(record.date_expiration,'%Y-%m-%d').date()
				record.warning_delta = (expiration - today -timedelta(days=31)).total_seconds()/86400
	
	@api.depends('ref_com')
	def _compute_expiration_delta(self):
		for record in self:
			if record.date_expiration:
				today = date.today()
				expiration = datetime.strptime(record.date_expiration,'%Y-%m-%d').date()
				record.expiration_delta = (expiration - today).total_seconds()/86400
				
	@api.onchange('date_utilisation')
	def change_statut(self):
		for record in self:
			if record.date_utilisation:
				record.statut='utilise'
			else:
				record.statut='dispo'
			
	@api.multi
	def check_validity(self):
		print("appel")
		result = self.env['bon.cadeau'].search([('statut','=','dispo')])
		for bon_cadeau in result:
			print("boucle")
			if bon_cadeau.expiration_delta<0:
				print("expired")
				bon_cadeau.statut = 'expire'
			if True:
				print("mail")
				template = self.env.ref('custom_gift_card.bon_cadeau_expiration')
				self.env['mail.template'].browse(template.id).send_mail(bon_cadeau.id)
	