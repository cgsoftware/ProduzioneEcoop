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

class mrp_bom_gruppi_comp(osv.osv):
    _name="mrp.bom.gruppi.comp"
    _description = 'Bill Of Material group component selection'    
    _columns = {
                'name':fields.char('Nome Gruppo Componente',size=25),
                }
 
mrp_bom_gruppi_comp()




class mrp_bom_altern_comp(osv.osv):
    _name="mrp.bom.altern.comp"
    _description = 'Bill Of Material component selection'    

    def _giacenza(self, cr, uid, ids, name, args, context=None):
        res = {}
        
        #import pdb;pdb.set_trace()
        if ids:
         for bom_line in self.browse(cr, uid, ids, context=context):
            res[bom_line.id] = {
                'giacenza': 0.0,
            }
            #for line in bom_line.product_id:
            line =  bom_line.product_id
            res[bom_line.id]['giacenza'] += line.qty_available
        return res
    
    
    _columns = {
                'bom_id': fields.many2one('mrp.bom', 'Parent BoM', ondelete='cascade', select=True),
                'product_id': fields.many2one('product.product', 'Componente', required=True),
                'product_uom': fields.many2one('product.uom', 'Product UOM', required=True),
                'product_qty': fields.float('Product Qty', required=True),      
                'gruppo': fields.many2one('mrp.bom.gruppi.comp', 'Gruppo', required=True),
                'priorita':fields.selection(_priorita, 'Priorità'),
                'routing_id': fields.many2one('mrp.routing', 'Routing' , required=True ),
                'fase_routing':fields.many2one('mrp.routing.workcenter', 'Lavorazione', required=False),
                'comp_obbl':fields.boolean('Obbligatorio'),
                'note':fields.char('Note', size=64),
                'flag_duplica':fields.boolean('Duplica'),
                'giacenza': fields.function(_giacenza, method=True, type='float' , string='Giacenza', store=False,multi='all'),
                
                         
                }
    _order = 'fase_routing,gruppo,priorita'

    def default_get(self, cr, uid, fields, context=None):
        #import pdb;pdb.set_trace()
        data = super(mrp_bom_altern_comp, self).default_get(cr, uid, fields, context=context)
        data['routing_id']=context.get('routing_id')
        return data

    
    def onchange_product_id(self, cr, uid, ids, product_id, name, context=None):
        """ Changes UoM and name if product_id changes.
        @param name: Name of the field
        @param product_id: Changed product_id
        @return:  Dictionary of changed values
        """
        if context is None:
            context = {}
            context['lang'] = self.pool.get('res.users').browse(cr,uid,uid).context_lang
            
        if product_id:
            prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            v = {'product_uom': prod.uom_id.id}
            if not name:
                v['name'] = prod.name
            return {'value': v}
        return {}
    


mrp_bom_altern_comp()

class mrp_bom_facoltativi_comp(osv.osv):
    _name="mrp.bom.facoltativi.comp"
    _description = 'Componenti possibili ma non obbligatori'    
#    def _sel_func(self, cr, uid, context={}):
#        obj = self.pool.get("mrp.routing.workcenter")
#        ids = obj.search(cr, uid, [])
#        res = obj.read(cr, uid, ids, ['name', 'id'], context)
#        res = [(r['id'], r['name']) for r in res]
#        return res
    
    def _giacenza(self, cr, uid, ids, name, args, context=None):
        res = {}
        
        #import pdb;pdb.set_trace()
        if ids:
         for bom_line in self.browse(cr, uid, ids, context=context):
            res[bom_line.id] = {
                'giacenza': 0.0,
            }
            #for line in bom_line.product_id:
            line =  bom_line.product_id
            res[bom_line.id]['giacenza'] += line.qty_available
        return res
    
    _columns = {
                'bom_id': fields.many2one('mrp.bom', 'Parent BoM', ondelete='cascade', select=True),
                'product_id': fields.many2one('product.product', 'Componenete', required=True),
                'product_uom': fields.many2one('product.uom', 'Product UOM', required=True),
                'product_qty': fields.float('Product Qty', required=False),      
                # 'gruppo': fields.many2one('mrp.bom.gruppi.comp', 'Gruppo', required=True),
                # 'priorita':fields.selection(_priorita, 'Priorità'),
                'routing_id': fields.many2one('mrp.routing', 'Routing' , required=True ),
                'fase_routing':fields.many2one('mrp.routing.workcenter', 'Lavorazione', required=True),
                'note':fields.char('Note', size=64),
                'flag_duplica':fields.boolean('Duplica'),
                'giacenza': fields.function(_giacenza, method=True, type='float' , string='Giacenza', store=False,multi='all'),
                # 'comp_obbl':fields.boolean('Obbligatorio'),
                }
    _order = 'fase_routing'
    
    def onchange_product_id(self, cr, uid, ids, product_id, name, context=None):
        """ Changes UoM and name if product_id changes.
        @param name: Name of the field
        @param product_id: Changed product_id
        @return:  Dictionary of changed values
        """
        if context is None:
            context = {}
            context['lang'] = self.pool.get('res.users').browse(cr,uid,uid).context_lang
            
        if product_id:
            prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            v = {'product_uom': prod.uom_id.id}
            if not name:
                v['name'] = prod.name
            return {'value': v}
        return {}
    
    def default_get(self, cr, uid, fields, context=None):
        #import pdb;pdb.set_trace()
        data = super(mrp_bom_facoltativi_comp, self).default_get(cr, uid, fields, context=context)
        data['routing_id']=context.get('routing_id')
        return data
    


mrp_bom_facoltativi_comp()

#
# Dimensions Definition
#
class mrp_bom(osv.osv):
    _inherit = "mrp.bom"
    
    def _giacenza(self, cr, uid, ids, name, args, context=None):
        res = {}
        
        #import pdb;pdb.set_trace()
        if ids:
         for bom_line in self.browse(cr, uid, ids, context=context):
            res[bom_line.id] = {
                'giacenza': 0.0,
            }
            #for line in bom_line.product_id:
            line =  bom_line.product_id
            res[bom_line.id]['giacenza'] += line.qty_available
        return res
    
    
    _columns = {
                'giacenza': fields.function(_giacenza, method=True, type='float' , string='Giacenza', store=False,multi='all'),
                'components_facolt':fields.one2many('mrp.bom.facoltativi.comp', 'bom_id', 'Righe Componenti Facoltativi'),
                'components_opt':fields.one2many('mrp.bom.altern.comp', 'bom_id', 'Righe Componenti Alternativi'),
                'routing_id2': fields.many2one('mrp.routing', 'Routing' , required=False ),
                'fase_routing':fields.many2one('mrp.routing.workcenter', 'Lavorazione', required=False),
                'comp_obbl':fields.boolean('Obbligatorio'),
                'note':fields.char('Note', size=64),                
                'flag_duplica':fields.boolean('Duplica'),
                }
    
    
    _order = 'fase_routing'
    
    
    
    def default_get(self, cr, uid, fields, context=None):
        #import pdb;pdb.set_trace()
        data = super(mrp_bom, self).default_get(cr, uid, fields, context=context)
        data['routing_id2']=context.get('routing_id')
        return data


    
    def _bom_explode(self, cr, uid, bom, factor, properties=[], addthis=False, level=0,routing_id=False):
        """ Finds Products and Workcenters for related BoM for manufacturing order.
        @param bom: BoM of particular product.
        @param factor: Factor of product UoM.
        @param properties: A List of properties Ids.
        @param addthis: If BoM found then True else False.
        @param level: Depth level to find BoM lines starts from 10.
        @return: result: List of dictionaries containing product details.
                 result2: List of dictionaries containing workcenter details.
        """
        factor = factor / (bom.product_efficiency or 1.0)
        factor = rounding(factor, bom.product_rounding)
        if factor < bom.product_rounding:
            factor = bom.product_rounding
        result = []
        result2 = []
        phantom = False
        if bom.type == 'phantom' and not bom.bom_lines:
            newbom = self._bom_find(cr, uid, bom.product_id.id, bom.product_uom.id, properties)
            if newbom:
                res = self._bom_explode(cr, uid, self.browse(cr, uid, [newbom])[0], factor*bom.product_qty, properties, addthis=True, level=level+10)
                result = result + res[0]
                result2 = result2 + res[1]
                phantom = True
            else:
                phantom = False
        #import pdb;pdb.set_trace()
        if not phantom:
            if addthis and not bom.bom_lines:
                result.append(
                {
                    'name': bom.product_id.name,
                    'product_id': bom.product_id.id,
                    'product_qty': bom.product_qty * factor,
                    'product_uom': bom.product_uom.id,
                    'product_uos_qty': bom.product_uos and bom.product_uos_qty * factor or False,
                    'product_uos': bom.product_uos and bom.product_uos.id or False,
                })
            rout = False
            if routing_id:
                rout= routing_id
            else:
             if bom.routing_id:
                 rout = bom.routing_id
            if rout:
                 
                for wc_use in rout.workcenter_lines:
                    wc = wc_use.workcenter_id
                    d, m = divmod(factor, wc_use.workcenter_id.capacity_per_cycle)
                    mult = (d + (m and 1.0 or 0.0))
                    cycle = mult * wc_use.cycle_nbr
                    result2.append({
                        'name': tools.ustr(wc_use.name) + ' - '  + tools.ustr(bom.product_id.name),
                        'workcenter_id': wc.id,
                        'sequence': level+(wc_use.sequence or 0),
                        'cycle': cycle,
                        'hour': float(wc_use.hour_nbr*mult + ((wc.time_start or 0.0)+(wc.time_stop or 0.0)+cycle*(wc.time_cycle or 0.0)) * (wc.time_efficiency or 1.0)),
                        'fase_routing':wc_use.id, #AGGIUNTO PER RIPORTARE  I DATI GIUSTI SULLE LINEE DI LAVORAZIONE IL RESTO DELLE DEF È STANDARD
                    })
            for bom2 in bom.bom_lines:
                res = self._bom_explode(cr, uid, bom2, factor, properties, addthis=True, level=level+10)
                result = result + res[0]
                result2 = result2 + res[1]
        return result, result2


    
mrp_bom()

