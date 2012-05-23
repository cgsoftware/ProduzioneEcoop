# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################



from datetime import datetime
from osv import osv, fields
from tools.translate import _
import netsvc
import time
import tools


def rounding(f, r):
    if not r:
        return f
    return round(f / r) * r

def _priorita(self, cr, uid, context={}):
     res = []
     for i in range(1,10):
         res.append((str(i).strip(),str(i).strip()))
    
     return res



class import_bomdett(osv.osv_memory):
    _name = 'import.bomdett'
    _description = 'Permette di importare i dettagli distinta base da altre distinte'
    _columns = {
                'numdist':fields.many2one('mrp.bom', 'Parent BoM', ondelete='cascade', select=True),
                'flg_std':fields.boolean('Dettaglio Standard'),
                'flg_opt':fields.boolean('Dettaglio Opzionali'),
                'flg_fac':fields.boolean('Dettaglio Facoltativi'),
                }
    
    def run_import(self, cr, uid, ids, context=None, automatic=False, use_new_cursor=False, ):
        #import pdb;pdb.set_trace()
        if context is None:
            context = {}
        
        import_data = self.browse(cr, uid, ids)[0] 
        id_dist_act = context.get('active_id',False)
        if import_data.numdist and  id_dist_act:
            #if True: #use_new_cursor:
                #use_new_cursor= use_new_cursor[0]         
                # cr = pooler.get_db(use_new_cursor).cursor()
      


                    if True: #use_new_cursor:
                        #cr = pooler.get_db(use_new_cursor).cursor()
                        dist_act_obj = self.pool.get('mrp.bom').browse(cr,uid,id_dist_act)
                        dist_cp_obj = self.pool.get('mrp.bom').browse(cr,uid,import_data.numdist.id)
                        if import_data.flg_opt:
                            for riga in dist_cp_obj.components_opt:
                                row = {
                                       'bom_id': id_dist_act,
                                       'product_id': riga.product_id.id,
                                       'product_uom': riga.product_uom.id,
                                       'product_qty': riga.product_qty,      
                                       'gruppo': riga.gruppo.id,
                                       'priorita':riga.priorita,
                                       'fase_routing':riga.fase_routing.id,
                                       'comp_obbl':riga.comp_obbl,
                                       'note':riga.note,                                      
                                       }
                                ok = self.pool.get('mrp.bom.altern.comp').create(cr,uid,row)
                        if import_data.flg_fac:
                            for riga in dist_cp_obj.components_facolt:
                                row = {
                                       'bom_id': id_dist_act,
                                       'product_id': riga.product_id.id,
                                       'product_uom': riga.product_uom.id,
                                       'product_qty': riga.product_qty,      
                                       #'gruppo': riga.gruppo.id,
                                       #'priorita':riga.priorita,
                                       'fase_routing':riga.fase_routing.id,
                                       #'comp_obbl':riga.comp_obbl,
                                       'note':riga.note,                                      
                                       }
                                ok = self.pool.get('mrp.bom.facoltativi.comp').create(cr,uid,row)
                        if import_data.flg_std:
                            for riga in dist_cp_obj.bom_lines:
                                row = {
                                       'bom_id': id_dist_act,
                                       'name':riga.product_id.default_code,
                                       'product_id': riga.product_id.id,
                                       'product_uom': riga.product_uom.id,
                                       'product_qty': riga.product_qty,      
                                       #'gruppo': riga.gruppo.id,
                                       #'priorita':riga.priorita,
                                       'fase_routing':riga.fase_routing.id,
                                       'comp_obbl':riga.comp_obbl,
                                       'note':riga.note,                                      
                                       }
                                ok = self.pool.get('mrp.bom').create(cr,uid,row)
 
                        
                  
        
        return {'type': 'ir.actions.act_window_close'}
import_bomdett()

    
