odoo.define('custom_gift_card.pos.models.amount', function (require) {
"use strict";

var models = require('point_of_sale.models');
var utils = require('web.utils');

var _super_posmodel = models.PosModel.prototype;

models.PosModel = models.PosModel.extend({
    initialize: function (session, attributes) {
		this.bind('change:selectedClient',this.watch_client,this);
        // Inheritance
        return _super_posmodel.initialize.call(this, session, attributes);
    },
	
	watch_client : function(){
		$('.test').text("0"); 
		if(this.changed.selectedClient!=null && this.changed.selectedClient!=undefined){
			this.clientId = this.changed.selectedClient['id'];
			var url = window.location.origin+"/web/dataset/call_kw/bon.cadeau/search_read";
			var params = {
				"args":[],
				"kwargs":{
					"context":{"lang":"fr_FR","tz":false,"uid":1},
					"domain":[["user_id","=",this.clientId]],
					"fields":["amount_left"],
				},
				"method":"search_read",
				"model":"bon.cadeau"
			};
			var total_bon = 0;
			this.attributes.rpc(url,params).then((value)=>{
				for(var i = 0;i<value.length;i++){
					total_bon = total_bon + value[i].amount_left;
				}
				this.db.partner_by_id[this.clientId].amount_bon_cadeau=total_bon;
				$('.test').text(total_bon); 
			});
			
		}
		
	},
    
});

});

