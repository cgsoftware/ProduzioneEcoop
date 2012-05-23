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

from tools.translate import _
from datetime import datetime
from osv import fields, osv


import netsvc
import time
from datetime import datetime


def _priorita(self, cr, uid, context={}):
     res = []
     for i in range(1,10):
         res.append((str(i).strip(),str(i).strip()))
    
     return res


## GESTIONE DELLE LAVORAZIONI CON RIPORTO DELLE DISTINTE BASI COME ORGANIZZATE

class mrp_wkl_standard_comp(osv.osv):
    _name="mrp.wkl.standard.comp"
    _description = 'Bill Of Material component selection'    
    _columns = {
                'lavorazione_id': fields.many2one('mrp.production.workcenter.line', 'Linea di Lavorazione', ondelete='cascade', select=True),
                'product_id': fields.many2one('product.product', 'Componente', required=True),
                'product_tmpl_id':fields.related('product_id', 'product_tmpl_id', string='Template', type='many2one', relation='product.template'),
                'product_uom': fields.many2one('product.uom', 'Product UOM', required=True),
                'product_qty': fields.float('Product Qty', required=True),      
                'fase_routing':fields.many2one('mrp.routing.workcenter', 'Lavorazione', required=False),
                'comp_obbl':fields.boolean('Obbligatorio'),
                'note':fields.char('Note', size=64),
                'flg_lavor':fields.boolean('Prelevato da Mag'),
                }
    _order = 'fase_routing,gruppo,priorita'
    
    def onchange_product_qty(self, cr, uid, ids, product_qty, context=None):
        
         return {'value':{'flg_lavor':True}}
                 
     
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
    


mrp_wkl_standard_comp()

class mrp_wkl_altern_comp(osv.osv):
    _name="mrp.wkl.altern.comp"
    _description = 'Bill Of Material component selection'    

    
    
    _columns = {
                'lavorazione_id': fields.many2one('mrp.production.workcenter.line', 'Linea di Lavorazione', ondelete='cascade', select=True),
                'product_id': fields.many2one('product.product', 'Componente', required=True),
                'product_tmpl_id':fields.related('product_id', 'product_tmpl_id', string='Template', type='many2one', relation='product.template'),
                'product_uom': fields.many2one('product.uom', 'Product UOM', required=True),
                'product_qty': fields.float('Product Qty', required=True),      
                'gruppo': fields.many2one('mrp.bom.gruppi.comp', 'Gruppo', required=True),
                'priorita':fields.selection(_priorita, 'Priorità'),
                'fase_routing':fields.many2one('mrp.routing.workcenter', 'Lavorazione', required=False),
                'comp_obbl':fields.boolean('Obbligatorio'),
                'note':fields.char('Note', size=64),
                'flg_lavor':fields.boolean('Prelevato da Mag'),
                'seller_ids': fields.many2one('product.supplierinfo', 'Fornitore'),
                'ragsoc':fields.related('seller_ids', 'name', string='Ragione Sociale', type='many2one', relation='res.partner',readonly=True),
                'num_doc':fields.char('Documento', size=30),

                
                         
                }
    _order = 'fase_routing,gruppo,priorita'

    def onchange_product_qty(self, cr, uid, ids, product_qty, context=None):
         return {'value':{'flg_lavor':True}}
    
    
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
    


mrp_wkl_altern_comp()

class mrp_wkl_facoltativi_comp(osv.osv):
    _name="mrp.wkl.facoltativi.comp"
    _description = 'Componenti possibili ma non obbligatori'    
    _columns = {
                'lavorazione_id': fields.many2one('mrp.production.workcenter.line', 'Linea di Lavorazione', ondelete='cascade', select=True),
                'product_id': fields.many2one('product.product', 'Componente', required=True),
                'product_tmpl_id':fields.related('product_id', 'product_tmpl_id', string='Template', type='many2one', relation='product.template'),                                  
                'product_uom': fields.many2one('product.uom', 'Product UOM', required=True),
                'product_qty': fields.float('Product Qty', required=False),      
                # 'gruppo': fields.many2one('mrp.bom.gruppi.comp', 'Gruppo', required=True),
                # 'priorita':fields.selection(_priorita, 'Priorità'),
                'fase_routing':fields.many2one('mrp.routing.workcenter', 'Lavorazione', required=False),
                'note':fields.char('Note', size=64),
                'flg_lavor':fields.boolean('Prelevato da Mag'),
                # 'comp_obbl':fields.boolean('Obbligatorio'),
                'seller_ids': fields.many2one('product.supplierinfo', 'Fornitore'),
                'ragsoc':fields.related('seller_ids', 'name', string='Ragione Sociale', type='many2one', relation='res.partner',readonly=True),
                'num_doc':fields.char('Documento', size=30),
                
                }
    _order = 'fase_routing'
    
    def onchange_product_qty(self, cr, uid, ids, product_qty, context=None):
         return {'value':{'flg_lavor':True}}
    
    
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
    


mrp_wkl_facoltativi_comp()

class mrp_des_difetti(osv.osv):
    _name="mrp.des.difetti"
    _description = 'Descrizione dei difetti rilevati in test'    
    _columns = {
                'name':fields.char('Note Difetto',size=128),
                }
 
mrp_des_difetti()

class mrp_wkl_des_difetti(osv.osv):
    _name="mrp.wkl.des.difetti"
    _description = 'Elenco dei difetti rilevati in test'    
    _columns = {
                'lavorazione_id': fields.many2one('mrp.production.workcenter.line', 'Linea di Lavorazione', ondelete='cascade', select=True),
                'id_difetto':fields.many2one('mrp.des.difetti', 'Difetto', required=False), 
                'nota':fields.char('Note Difetto',size=128),
                }
 
mrp_wkl_des_difetti()



class mrp_routing_workcenter(osv.osv):
    """
    Defines working cycles and hours of a workcenter using routings.
    """
    _inherit = 'mrp.routing.workcenter'
    
    _order = 'sequence,workcenter_id'



mrp_routing_workcenter()

class mrp_production_product_line(osv.osv):
    _inherit = 'mrp.production.product.line'
    _columns = {
                'move_creato':fields.boolean('Move di Scarico Creato'),
                }
    
    _defaults = {
                 'move_creato':False,
                 }
    
mrp_production_product_line()    

class mrp_production_workcenter_line(osv.osv):
    _inherit = 'mrp.production.workcenter.line'
    _columns = {
                'components_facolt':fields.one2many('mrp.wkl.facoltativi.comp', 'lavorazione_id', 'Righe Componenti Facoltativi',readonly=True, states={'startworking': [('readonly', False)]}),
                'components_altern':fields.one2many('mrp.wkl.altern.comp', 'lavorazione_id', 'Righe Componenti Opzionali',readonly=True, states={'startworking': [('readonly', False)]}),
                'components_standard':fields.one2many('mrp.wkl.standard.comp', 'lavorazione_id', 'Righe Componenti Standard',readonly=True, states={'startworking': [('readonly', False)]}),
                'test_difetti':fields.one2many('mrp.wkl.des.difetti', 'lavorazione_id', 'Difetti',readonly=True, states={'startworking': [('readonly', False)]}),
                'fase_routing':fields.many2one('mrp.routing.workcenter', 'Lavorazione', required=False),
                }

    def action_start_working(self, cr, uid, ids):
     """ Sets state to start working and writes starting date.
        @return: True
        """
     res = {}
     #import pdb;pdb.set_trace()
     if ids:
        if len(ids)==1:
           
            wkl_rec = self.browse(cr,uid,ids)[0]
            if wkl_rec.sequence > 0:
                cerca = [('production_id','=',wkl_rec.production_id.id),('sequence','=',wkl_rec.sequence-1)]
                id_prec = self.search(cr,uid,cerca)
                if id_prec:
                    if self.browse(cr,uid,id_prec[0]).state<>'done':
                        raise osv.except_osv(_('ERRORE !'), _('La Fase Precedente Non Sembra Completata'))
                        return True                        
            for riga_lav in self.browse(cr,uid,ids):
                if riga_lav.product:
                    cerca = [('product_id','=',riga_lav.product.id),('bom_id','=',None)]
                    distinta_ids = self.pool.get('mrp.bom').search(cr,uid,cerca)
                    if distinta_ids:
                        distinta = self.pool.get('mrp.bom').browse(cr,uid,distinta_ids)[0]
                        # SCRIVE RIGHE STANDARD
                        if not riga_lav.components_standard:
                            for riga_comp in distinta.bom_lines:
                             if riga_comp.fase_routing.id == riga_lav.fase_routing.id:
                                #import pdb;pdb.set_trace()
                                if riga_lav.qty*riga_comp.product_qty>riga_comp.product_id.qty_available and riga_comp.product_id.type=='product':
                                    # articolo stoccabile e giacenza insufficiente
                                    raise osv.except_osv(_('ERRORE !'), _('NON PUOI AVVIARE LA LAVORAZIONE, GIACENZA COMPONENTE '+ riga_comp.product_id.default_code  +' INSUFFICIENTE'))
                                else:
                                    riga = {
                                        'lavorazione_id':riga_lav.id,                                        
                                        'product_id': riga_comp.product_id.id,
                                        'product_uom': riga_comp.product_uom.id,
                                        'product_qty': riga_lav.qty*riga_comp.product_qty,      
                                        'fase_routing':riga_comp.fase_routing.id,
                                        'comp_obbl':riga_comp.comp_obbl,
                                        'note':riga_comp.note,
                                        'flg_lavor':False,                                       
                                        }
                                    id_comp = self.pool.get('mrp.wkl.standard.comp').create(cr,uid,riga)
                                    
                        if not riga_lav.components_facolt:
                          if riga_comp.fase_routing.id == riga_lav.fase_routing.id:
                            for riga_comp in distinta.components_facolt:
                                riga = {
                                        'lavorazione_id':riga_lav.id,                                        
                                        'product_id': riga_comp.product_id.id,
                                        'product_uom': riga_comp.product_uom.id,
                                        'product_qty': riga_lav.qty*riga_comp.product_qty,      
                                        'fase_routing':riga_comp.fase_routing.id,
                                        'note':riga_comp.note,
                                        'flg_lavor':False,                                       
                                        }
                                id_comp = self.pool.get('mrp.wkl.facoltativi.comp').create(cr,uid,riga)
                        if not riga_lav.components_altern:
                            lista_record= self.prepara_records(cr,uid,distinta, riga_lav)
                            if lista_record:
                              for riga in lista_record:
                                  
 #                               riga = {
 #                                       'lavorazione_id':riga_lav.id,                                        
 #                                       'product_id': riga_comp.product_id.id,
 #                                       'product_uom': riga_comp.product_uom.id,
 #                                       'product_qty': riga_lav.qty*riga_comp.product_qty,   
 #                                       'gruppo': riga_comp.gruppo.id,
 #                                       'priorita':riga_comp.priorita,                                           
 #                                       'fase_routing':riga_comp.fase_routing.id,
 #                                       'comp_obbl':riga_comp.comp_obbl,
 #                                       'note':riga_comp.note,
 #                                       'flg_lavor':False,                                       
 #                                       }
                                id_comp = self.pool.get('mrp.wkl.altern.comp').create(cr,uid,riga)
            res = super(mrp_production_workcenter_line,self).action_start_working(cr, uid, ids)                
        else:
            pass
            raise osv.except_osv(_('ERRORE !'), _('NON PUOI AVVIARE + LAVORAZIONI CONTEMPORANEAMENTE'))
            return True
     
     return res

    def prepara_records(self,cr,uid,distinta,riga_lav,context=None):
           #import pdb;pdb.set_trace()
           lst = []
           gruppo_ids = self.pool.get('mrp.bom.gruppi.comp').search(cr,uid,[])
           for gruppo_id in gruppo_ids:
               grup = self.pool.get('mrp.bom.gruppi.comp').browse(cr,uid,gruppo_id)
               cr.execute('SELECT product_id, product_uom , product_qty,gruppo,priorita,fase_routing,comp_obbl,note FROM mrp_bom_altern_comp ' \
                    'WHERE bom_id = %s AND gruppo = %s AND fase_routing = %s' \
                    'ORDER BY priorita ASC ',
                    (distinta.id, gruppo_id,riga_lav.fase_routing.id))
               res = cr.fetchall()             
               if res:
                   #import pdb;pdb.set_trace()
                   totqt = riga_lav.qty
                   for record in res:
                       componente = self.pool.get('product.product').browse(cr,uid,record[0]) 
                       qta = record[2]
                       real=0
                       if totqt*qta <= componente.qty_available: #Giacenza a sufficenza basta la prima riga
                           real = totqt*qta
                       else:
                           real = componente.qty_available/qta # calcola il realizzabile
                       riga = {
                                        'lavorazione_id':riga_lav.id,                                        
                                        'product_id': componente.id,
                                        'product_uom': record[1],
                                        'product_qty': real,   
                                        'gruppo': record[3],
                                        'priorita':record[4],                                           
                                        'fase_routing':record[5],
                                        'comp_obbl':record[6],
                                        'note':record[7],
                                        'flg_lavor':False,                                                                      
                               }
                       lst.append(riga)    
                       totqt -= real
                   if totqt>0:
                            raise osv.except_osv(_('ERRORE !'), _('NON CI SONO GIACENZE SUFFICIENTI PER IL GRUPPO '+grup.name))
           return lst

    def action_done(self, cr, uid, ids):
        """ Sets state to done, writes finish date and calculates delay.
        @return: True
        """
        prod_line_obj = self.pool.get('mrp.production.product.line')
        #import pdb;pdb.set_trace()
        if ids:
            date_now = time.strftime('%Y-%m-%d %H:%M:%S')
            scritto = False
            for riga_lav in self.browse(cr,uid,ids):
                if riga_lav.production_id:
                    # PRIMA LE FACOLTATIVE
                    production = riga_lav.production_id
                    source = production.product_id.product_tmpl_id.property_stock_production.id
                    for line in riga_lav.components_facolt:
                        if line.flg_lavor: # ok è una riga lavorata
                            moves = []
                            move_id = False
                            newdate = datetime.strptime(date_now,'%Y-%m-%d %H:%M:%S')                           
                            # qui non c'è nulla di obbliatorio quindi prende tutto ciò che dice lavorato
                            riga_prod= {
                                        'name':'PROD:' + production.name,
                                        'product_id': line.product_id.id,
                                        'product_qty': line.product_qty,
                                        'product_uom': line.product_uom.id,
                                        'production_id':production.id,
                                        'move_creato':False,                                
                                        }
                            id_prod_line = prod_line_obj.create(cr,uid,riga_prod)
                            scritto = True
                    for line in riga_lav.components_altern:
                        if line.flg_lavor: # ok è una riga lavorata
                            moves = []
                            move_id = False
                            newdate = datetime.strptime(date_now,'%Y-%m-%d %H:%M:%S')                           
                            # qui non c'è nulla di obbliatorio quindi prende tutto ciò che dice lavorato
                            riga_prod= {
                                        'name':'PROD:' + production.name,
                                        'product_id': line.product_id.id,
                                        'product_qty': line.product_qty,
                                        'product_uom': line.product_uom.id,
                                        'production_id':production.id,
                                        'move_creato':False,                                
                                        }
                            id_prod_line = prod_line_obj.create(cr,uid,riga_prod)
                            scritto = True
                    for line in riga_lav.components_standard:
                        if line.flg_lavor: # ok è una riga lavorata
                            moves = []
                            move_id = False
                            newdate = datetime.strptime(date_now,'%Y-%m-%d %H:%M:%S')                           
                            # qui non c'è nulla di obbliatorio quindi prende tutto ciò che dice lavorato
                            riga_prod= {
                                        'name':'PROD:' + production.name,
                                        'product_id': line.product_id.id,
                                        'product_qty': line.product_qty,
                                        'product_uom': line.product_uom.id,
                                        'production_id':production.id,
                                        'move_creato':False,                                
                                        }
                       # id_prod_line = prod_line_obj.create(cr,uid,riga_prod)
                    
                            scritto = True
                    if riga_lav.test_difetti:
                        context = {}
                        qty_new = production.product_qty -len(riga_lav.test_difetti)
                        split = self.action_split_order(cr, uid, production.id,len(riga_lav.test_difetti),context)
                        #QUI ADEGUA LE RIGHE LE LINEE DI PRODUZIONE NON ANCORA LAVORATE
                        for rig in production.workcenter_lines:
                            if rig.state == 'draft':
                                self.write(cr,uid,rig.id,{'qty':qty_new})
                                
                                
                        
                if scritto:
                    for riga_lav in self.browse(cr,uid,ids):
                        production = riga_lav.production_id                      
                        self.action_agg_production(cr, uid, [production.id])
        
        res = super(mrp_production_workcenter_line,self).action_done(cr, uid, ids)
        oper_ids = self.search(cr,uid,[('production_id','=',production.id)])
        #production = self.pool.get('mrp.production').browse(cr,uid,production.id)
        obj = self.browse(cr,uid,oper_ids)        
        flag = True
        #import pdb;pdb.set_trace()
        for line in obj:
            if line.state != 'done':
                flag = False
        if flag:                
                ok = self.pool.get('mrp.production').action_produce(cr, uid, production.id, production.product_qty, 'consume_produce')
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'mrp.production', production.id, 'button_produce_done', cr)
        
        return res
    
    
    def action_agg_production(self, cr, uid, ids): 

        res = {}
        moves = []
        date_now = time.strftime('%Y-%m-%d %H:%M:%S')
        move_obj = self.pool.get('stock.move')
        
        if ids:   
            for production in self.pool.get('mrp.production').browse(cr,uid,ids):
             moves = []
             for movim in production.move_lines2:
                    moves.append(movim.id)    
             #import pdb;pdb.set_trace()            
             for line in production.product_lines:
                move_id = False
                # newdate = production.date_planned
                newdate = datetime.strptime(date_now,'%Y-%m-%d %H:%M:%S')
                source = production.product_id.product_tmpl_id.property_stock_production.id
                res_final_id = production.move_created_ids[0].id
                if line.product_id.type in ('product', 'consu') and not line.move_creato:
                    
                    rig = {
                        'name':'PROD:' + production.name,
                        'date': newdate,
                        'product_id': line.product_id.id,
                        'product_qty': line.product_qty,
                        'product_uom': line.product_uom.id,
                        'product_uos_qty': line.product_uos and line.product_uos_qty or False,
                        'product_uos': line.product_uos and line.product_uos.id or False,
                        'location_id': production.location_src_id.id,
                        'location_dest_id': source,
                        'move_dest_id': res_final_id,
                        'state': 'done',
                        'company_id': production.company_id.id,
                    }
                    res_dest_id = move_obj.create(cr, uid,rig )
                    #import pdb;pdb.set_trace()
                    moves.append(res_dest_id)
                    self.pool.get('mrp.production.product.line').write(cr, uid, [line.id], {'move_creato':True})
             if moves:
                 self.pool.get('mrp.production').write(cr, uid, [production.id], {'move_lines': [(6,0,moves)]})   
        return res
    
    def action_split_order(self, cr, uid, id,quantity,context):
        #import pdb;pdb.set_trace()
        prod_obj = self.pool.get('mrp.production')
        production = self.pool.get('mrp.production').browse(cr, uid, id, context)
        if production.state != 'confirmed':
          #  raise osv.except_osv(_('Error !'), _('Production order "%s" is not in "Waiting Goods" state.') % production.name)
          pass
        if quantity >= production.product_qty:
            raise osv.except_osv(_('Error !'), _('Quantity must be greater than production quantity in order "%s" (%s / %s)') % (production.name, quantity, production.product_qty))

        # Create new production, but ensure product_lines is kept empty.
        new_production_id = prod_obj.copy(cr, uid, id, {
            'product_lines': [],
            'move_prod_id': False,
            'product_qty':  quantity,
        }, context)

        prod_obj.write(cr, uid, production.id, {
            'product_qty': production.product_qty - quantity,
            #'product_lines': [],
        }, context)

        prod_obj.action_compute(cr, uid, [ new_production_id])
        #prod_obj.write(cr, uid, prod.id, {'product_qty' : quantity })
        #prod_obj._change_prod_qty( cr, uid, production.id ,production.product_qty-quantity, context)
        workflow = netsvc.LocalService("workflow")
        workflow.trg_validate(uid, 'mrp.production', new_production_id, 'button_confirm', cr)
        res=[]
        #res = self.pool.get('mrp.production')._split(cr,uid,ids,new_qty,context)
        if res:
           # picking_id = self.pool.get('mrp.production').action_confirm(cr, uid, [new_production_id])
            pass
        
        return True    
    
mrp_production_workcenter_line()


class mrp_production(osv.osv):
    _inherit = 'mrp.production'
    
    def action_compute(self, cr, uid, ids, properties=[]):
        """ Computes bills of material of a product.
        @param properties: List containing dictionaries of properties.
        @return: No. of products.
        """
        results = []
        bom_obj = self.pool.get('mrp.bom')
        prod_line_obj = self.pool.get('mrp.production.product.line')
        workcenter_line_obj = self.pool.get('mrp.production.workcenter.line')
        for production in self.browse(cr, uid, ids):
            cr.execute('delete from mrp_production_product_line where production_id=%s', (production.id,))
            cr.execute('delete from mrp_production_workcenter_line where production_id=%s', (production.id,))
            bom_point = production.bom_id
            bom_id = production.bom_id.id
            if not bom_point:
                bom_id = bom_obj._bom_find(cr, uid, production.product_id.id, production.product_uom.id, properties)
                if bom_id:
                    bom_point = bom_obj.browse(cr, uid, bom_id)
                    routing_id = bom_point.routing_id.id or False
                    self.write(cr, uid, [production.id], {'bom_id': bom_id, 'routing_id': routing_id})

            if not bom_id:
                raise osv.except_osv(_('Error'), _("Couldn't find bill of material for product"))

            factor = production.product_qty * production.product_uom.factor_inv / bom_point.product_uom.factor
            #import pdb;pdb.set_trace()
            res = bom_obj._bom_explode(cr, uid, bom_point, factor / bom_point.product_qty, properties, routing_id=production.routing_id)
            #import pdb;pdb.set_trace()
            results = res[0]
            results2 = res[1]
            for line in results:
                line['production_id'] = production.id
                prod_line_obj.create(cr, uid, line)
            for line in results2:
                line['production_id'] = production.id
                workcenter_line_obj.create(cr, uid, line)
        return len(results)


mrp_production()

