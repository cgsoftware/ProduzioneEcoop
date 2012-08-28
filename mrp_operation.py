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



from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import decimal_precision as dp
import time
import netsvc
import pooler, tools
import math
from tools.translate import _

from osv import fields, osv

def _priorita(self, cr, uid, context={}):
     res = []
     for i in range(1,10):
         res.append((str(i).strip(),str(i).strip()))
    
     return res


## GESTIONE DELLE LAVORAZIONI CON RIPORTO DELLE DISTINTE BASI COME ORGANIZZATE

class mrp_wkl_standard_comp(osv.osv):
    _name="mrp.wkl.standard.comp"
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
                'lavorazione_id': fields.many2one('mrp.production.workcenter.line', 'Linea di Lavorazione', ondelete='cascade', select=True),
                'product_id': fields.many2one('product.product', 'Componente', required=True),
                'product_tmpl_id':fields.related('product_id', 'product_tmpl_id', string='Template', type='many2one', relation='product.template'),
                'product_uom': fields.many2one('product.uom', 'Product UOM', required=True),
                'product_qty': fields.float('Product Qty', required=True),    
                'giacenza': fields.function(_giacenza, method=True, type='float' , string='Giacenza', store=False,multi='all'),  
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
                'lavorazione_id': fields.many2one('mrp.production.workcenter.line', 'Linea di Lavorazione', ondelete='cascade', select=True),
                'product_id': fields.many2one('product.product', 'Componente', required=True),
                'product_tmpl_id':fields.related('product_id', 'product_tmpl_id', string='Template', type='many2one', relation='product.template'),
                'product_uom': fields.many2one('product.uom', 'Product UOM', required=True),
                'product_qty': fields.float('Product Qty', required=True),      
                'giacenza': fields.function(_giacenza, method=True, type='float' , string='Giacenza', store=False,multi='all'),
                'gruppo': fields.many2one('mrp.bom.gruppi.comp', 'Gruppo', required=True),
                'priorita':fields.selection(_priorita, 'Priorità'),
                'fase_routing':fields.many2one('mrp.routing.workcenter', 'Lavorazione', required=False),
                'comp_obbl':fields.boolean('Obbligatorio'),
                'note':fields.char('Note', size=64),
                'flg_lavor':fields.boolean('Prelevato da Mag'),
                'flg_no_lavor':fields.boolean('Non Prelevare da Magazzino'),
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
                'lavorazione_id': fields.many2one('mrp.production.workcenter.line', 'Linea di Lavorazione', ondelete='cascade', select=True),
                'product_id': fields.many2one('product.product', 'Componente', required=True),
                'product_tmpl_id':fields.related('product_id', 'product_tmpl_id', string='Template', type='many2one', relation='product.template'),                                  
                'product_uom': fields.many2one('product.uom', 'Product UOM', required=True),
                'product_qty': fields.float('Product Qty', required=False),    
                'giacenza': fields.function(_giacenza, method=True, type='float' , string='Giacenza', store=False,multi='all'),  
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
                'qta_difett':fields.float('Qta Difettosa', required=False),
                'nota':fields.char('Note Difetto',size=128),
                'flag_genera_prod':fields.boolean('Produzione', help="Genera una nuova produzione per questo Difetto"),
                
                }
    _defaults={
               'qta_difett':1,
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
                'operatore_id':fields.many2one('res.users', 'Operatore', required=False),
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
            if not wkl_rec.operatore_id:
                    ok = self.write(cr,uid,ids,{'operatore_id':uid})
                        #raise osv.except_osv(_('ERRORE !'), _('La Inserire il Nome Operatore'))
                        #return True                        
                
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
                           real = totqt
                           # qtt= real
                       else:
                           real = int(componente.qty_available/qta) # calcola il realizzabile
                       qtt = qta*real
                       riga = {
                                        'lavorazione_id':riga_lav.id,                                        
                                        'product_id': componente.id,
                                        'product_uom': record[1],
                                        'product_qty': qtt,   
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
    
    def check_prelevato(self,cr,uid,ids):
        res = True
        gruppi={}
        for riga_lav in self.browse(cr,uid,ids):
                 for line in riga_lav.components_altern:
                     if gruppi.get(riga_lav.gruppo,False):
                         if line.flg_lavor: # ok è una riga lavorata
                             gruppi[riga_lav.gruppo]+=1
                     else:
                         gruppi.update({riga_lav.gruppo:0})
                         if line.flg_lavor: # ok è una riga lavorata
                             gruppi[riga_lav.gruppo]+=1
        for x in gruppi.values():
            if x ==0:
                raise osv.except_osv(_('ERRORE !'), _('CI SONO GRUPPI ARTICOLO NON LAVORATI CONTROLLA LE MATERIE PRIME DA UTILIZZARE '))  
        return res

    def action_done(self, cr, uid, ids):
        """ Sets state to done, writes finish date and calculates delay.
        @return: True
        """
        prod_line_obj = self.pool.get('mrp.production.product.line')
        #import pdb;pdb.set_trace()
        if ids:
            scritto = self.scarica_merci(cr,uid,ids)
            self.difetti(cr,uid,ids)
            if scritto:
                    for riga_lav in self.browse(cr,uid,ids):
                        production = riga_lav.production_id                      
                        self.action_agg_production(cr, uid, [production.id])
        
            res = super(mrp_production_workcenter_line,self).action_done(cr, uid, ids)
            for riga_lav in self.browse(cr,uid,ids):
                production = riga_lav.production_id
                oper_ids = self.search(cr,uid,[('production_id','=',production.id)])
                #production = self.pool.get('mrp.production').browse(cr,uid,production.id)
                obj = self.browse(cr,uid,oper_ids)        
                flag = True
                #import pdb;pdb.set_trace()
                for line in obj:
                    if line.state != 'done':
                        flag = False
                if flag:   
                # SE NON CI SONO ALTRE RIGHE DI LAVORAZIONE VA A CHIUDERE LA PRODUZIONE FACENDO DONE E AGGIORNANDO IL COSTO MEDIO             
                #ok = self.pool.get('mrp.production').action_produce(cr, uid, production.id, production.product_qty, 'consume_produce')
                #wf_service = netsvc.LocalService("workflow")
                #wf_service.trg_validate(uid, 'mrp.production', production.id, 'button_produce_done', cr)
                    riga = {
                        'product_qty':production.product_qty,
                        'mode':'consume_produce'                     
                        }
                    id_c = self.pool.get('mrp.product.produce').create(cr,uid,riga)
                    ctx={'active_ids':[production.id]}
                    okk = self.pool.get('mrp.product.produce').do_produce( cr, uid, [id_c], context=ctx)
        else:
            res = True
        return res
    
    def scarica_merci(self, cr, uid, ids):
            prod_line_obj = self.pool.get('mrp.production.product.line')
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
                    #if self.check_prelevato(cr, uid, ids):
                    #   pass
                    for line in riga_lav.components_altern: 
                        if line.product_qty>0:
                         if (line.flg_lavor or line.flg_no_lavor):
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
                         else:
                            raise osv.except_osv(_('ERRORE !'), _('CI SONO GRUPPI ARTICOLO SENZA SCELTA \n CONTROLLA LE MATERIE PRIME DA UTILIZZARE '))
                    for line in riga_lav.components_standard:
                        if line.flg_lavor: # ok è una riga lavorata
                            moves = []
                            move_id = False
                            newdate = datetime.strptime(date_now,'%Y-%m-%d %H:%M:%S')                           
                            # deve ciclare su production.product_lines a parità di articolo
                            # deve cambiare la qta
                            for ri in production.product_lines:
                                if ri.product_id.id == line.product_id.id:
                                        riga_prod= {
                                        'product_qty': line.product_qty,
                                            }
                                        ok = self.pool.get('mrp.production.product.line').write(cr,uid,[ri.id],riga_prod)
                       # id_prod_line = prod_line_obj.create(cr,uid,riga_prod)                    
                            scritto = True
        
        
            return scritto
    
    def difetti(self,cr,uid,ids):
            prod_line_obj = self.pool.get('mrp.production.product.line')
            date_now = time.strftime('%Y-%m-%d %H:%M:%S')
            scritto = False
            for riga_lav in self.browse(cr,uid,ids): 
                production = riga_lav.production_id   
                #import pdb;pdb.set_trace()    
                if riga_lav.test_difetti:
                        tot_difetti =0
                        qta_newp=0
                        for rr in riga_lav.test_difetti:
                            tot_difetti+=rr.qta_difett
                            if rr.flag_genera_prod:
                                    qta_newp+=rr.qta_difett
                        context = {}
                        qty_new = production.product_qty -tot_difetti
                        if qty_new == 0 : 
                            # tutti i difetti portano a zero la produzione utilizzare il bottone idoneo
                            raise osv.except_osv(_('Errore !'), _('Tutti i difetti portano a zero la produzione \n UTILIZZARE IL BOTTONE APPOSITO'))
                        else:                        
                            split = self.action_split_order(cr, uid, production.id,tot_difetti,qta_newp,context)
                        #QUI ADEGUA LE RIGHE LE LINEE DI PRODUZIONE NON ANCORA LAVORATE
                        for rig in production.workcenter_lines:
                            if rig.state == 'draft':
                                self.write(cr,uid,rig.id,{'qty':qty_new})

            return True
    
    def action_scratch(self, cr, uid, ids,context=False):
        # Annulla la produzione creando una operazione di costo addebitato sull'archivio
        prod_line_obj = self.pool.get('mrp.production.product.line')
        #import pdb;pdb.set_trace()
        res = True
        moves = []
        date_now = time.strftime('%Y-%m-%d %H:%M:%S')
        move_obj = self.pool.get('stock.move')
        newdate = datetime.strptime(date_now,'%Y-%m-%d %H:%M:%S')
        production = False
        if ids:
            if self.browse(cr,uid,ids)[0].state != 'cancel':
                scritto = self.scarica_merci(cr,uid,ids)
                if True : # scritto:
                  for riga_lav in self.browse(cr,uid,ids):
                   production = riga_lav.production_id                      
                   self.action_agg_production(cr, uid, [production.id])
                        
        #res = super(mrp_production_workcenter_line,self).action_done(cr, uid, ids)
        # HA RIPORTATO SULLA PRODUZIONE TUTTI GLI EVENTUALI ARICOLI SCARICATI. 
        # A QUESTO PUNTO CREA UN MOVIMENTO DI SCARICO DELLE MERCI ED AGGIORNA IL COSTO MEDIO DELL'ARTICOLO
        # ED ANNULLA LA PRODUZIONE PROGRAMMATA.
                   if production:
                    #import pdb;pdb.set_trace()
                    source = production.product_id.product_tmpl_id.property_stock_production.id
                    move_lines=[]
                    pick = {
                            'type':'internal',
                            'note':"Scarico per intera produzione difettosa "+production.product_id.default_code,
                            'origin':production.name,
                            'location_id':production.location_src_id.id,
                            'location_dest_id': source,
                            'state':'done',
                            'production_product__id':production.product_id.id,
                            'costo_medio_prima':production.product_id.standard_price
                            }
                    pick_id = self.pool.get('stock.picking').create(cr,uid,pick)
                    total_cost = 0
                    #import pdb;pdb.set_trace()
                    for line in production.move_lines2:
                        if line.product_id.type in ('product', 'consu'):
                    
                            rig = {
                        'name':'PROD:' + production.name,
                        'date': newdate,
                        'picking_id':pick_id,
                        'product_id': line.product_id.id,
                        'product_qty': line.product_qty,
                        'product_uom': line.product_uom.id,
                        'product_uos_qty': line.product_uos and line.product_uos_qty or False,
                        'product_uos': line.product_uos and line.product_uos.id or False,
                        'location_id': production.location_src_id.id,
                        'location_dest_id': source,
                        'price_unit':line.product_id.standard_price,
                        #'move_dest_id': res_final_id,
                        'state': 'done',
                        'company_id': production.company_id.id,
                        'note':"Scarico per intera produzione difettosa "+production.product_id.default_code,
                            }
                            res_dest_id = move_obj.create(cr, uid,rig )
                            total_cost+=line.product_qty*line.product_id.standard_price
                    #import pdb;pdb.set_trace()
                    if total_cost>0:

                        if production.product_id.cost_method == 'average':
                #import pdb;pdb.set_trace()
                            new_c_medio = ((production.product_id.standard_price* production.product_id.qty_available)+total_cost)/production.product_id.qty_available
                            print 'Standard ',production.product_id.standard_price
                            print 'Qty ',production.product_id.qty_available
                            print 'Costo ',total_cost
                            print "((production.product_id.standard_price* production.product_id.qty_available)+total_cost)/production.product_id.qty_available  = ",new_c_medio
                            riga_prod ={
                                        'standard_price':new_c_medio,
                                            }
                            ok = self.pool.get('product.product').write(cr,uid,[production.product_id.id],riga_prod)
                            riga_rep = {
                                        #'costo_medio_prima':production.product_id.standard_price,
                                        'new_c_medio':new_c_medio,
                        
                                        }                            
                            ok = self.pool.get('stock.picking').write(cr,uid,[pick_id],riga_rep)

                            
                    self.pool.get('mrp.production').action_cancel(cr,uid,[production.id])    # annullato ordine di produzione
            else:
                raise osv.except_osv(_('Error !'), _('Operazione Già Eseguita'))
                        
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
    
    def action_split_order(self, cr, uid, id,quantity_tot,quantity_new,context):
        #import pdb;pdb.set_trace()
        prod_obj = self.pool.get('mrp.production')
        production = self.pool.get('mrp.production').browse(cr, uid, id, context)
        if production.state != 'confirmed':
          #  raise osv.except_osv(_('Error !'), _('Production order "%s" is not in "Waiting Goods" state.') % production.name)
          pass
        if quantity_tot >= production.product_qty:
            raise osv.except_osv(_('Error !'), _('Quantity must be greater than production quantity in order "%s" (%s / %s)') % (production.name, quantity, production.product_qty))

        # Create new production, but ensure product_lines is kept empty.
        if quantity_new>0:
            new_production_id = prod_obj.copy(cr, uid, id, {
            'product_lines': [],
            'move_prod_id': False,
            'product_qty':  quantity_new,
            }, context)
        else:
            new_production_id=False


        prod_obj.write(cr, uid, production.id, {
            'product_qty': production.product_qty - quantity_tot,
            #'product_lines': [],
        }, context)
        for riga in production.move_created_ids:
            #import pdb;pdb.set_trace()
            rg = {
                  'product_qty':production.product_qty - quantity_tot
                  }
            ok = self.pool.get('stock.move').write(cr,uid,[riga.id],rg)
        if new_production_id:
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

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _columns ={
               'production_product__id': fields.many2one('product.product', 'Prodotto di Produzione di Origine', required=False ),   
               'costo_medio_prima':fields.float('Costo Unitario prima Produzione', digits=(9, 4) ),                           
               'new_c_medio':fields.float('Nuovo Costo Medio Articolo Prodotto',  digits=(9, 4) ),
               }


stock_picking()