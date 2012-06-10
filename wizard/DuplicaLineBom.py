# -*- encoding: utf-8 -*-


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
 
 
class duplica_line_bom(osv.osv_memory):
    _name = 'duplica_line_bom'
    _description = 'Permette di duplicare le linee di bom cambiandi routing e fase'
    _columns = {
                'routing_id': fields.many2one('mrp.routing', 'Routing' , required=True ),
                'fase_routing':fields.many2one('mrp.routing.workcenter', 'Lavorazione', required=True),
                }


    def run_import(self, cr, uid, ids, context=None, automatic=False, use_new_cursor=False, ):
        #import pdb;pdb.set_trace()
        if context is None:
            context = {}
        
        import_data = self.browse(cr, uid, ids)[0] 
        id_dist_act = context.get('active_id',False)
        distinta = self.pool.get('mrp.bom').browse(cr,uid,id_dist_act)
        # componenti obbligatori
        for bom_line in distinta.bom_lines:
            if bom_line.flag_duplica:
                vals = self.pool.get('mrp.bom').read(cr,uid,bom_line.id)
                vals['routing_id']= import_data.routing_id.id
                vals['fase_routing']= import_data.fase_routing.id
                vals['product_uom']=vals['product_uom'][0]
                vals['flag_duplica']=False 
                vals['id']=False
                vals['company_id']=vals['company_id'][0]
                vals['bom_id']=vals['bom_id'][0]
                vals['product_id']=vals['product_id'][0]
                
                
                id_line = self.pool.get('mrp.bom').create(cr,uid,vals)
                self.pool.get('mrp.bom').write(cr,uid,[bom_line.id],{'flag_duplica':False})
        # componenti facoltativi
        #import pdb;pdb.set_trace()
        for bom_line in distinta.components_facolt:
            if bom_line.flag_duplica:
                vals = self.pool.get('mrp.bom.facoltativi.comp').read(cr,uid,bom_line.id)
                vals['routing_id']= import_data.routing_id.id
                vals['fase_routing']= import_data.fase_routing.id
                vals['product_uom']=vals['product_uom'][0]
                vals['flag_duplica']=False 
                vals['id']=False
                
                vals['bom_id']=vals['bom_id'][0]
                vals['product_id']=vals['product_id'][0]
                
                id_line = self.pool.get('mrp.bom.facoltativi.comp').create(cr,uid,vals)
                self.pool.get('mrp.bom.facoltativi.comp').write(cr,uid,[bom_line.id],{'flag_duplica':False})
        # componenti opzionali
        #import pdb;pdb.set_trace()
        for bom_line in distinta.components_opt:
            if bom_line.flag_duplica:
                vals = self.pool.get('mrp.bom.altern.comp').read(cr,uid,bom_line.id)
                vals['routing_id']= import_data.routing_id.id
                vals['fase_routing']= import_data.fase_routing.id
                vals['product_uom']=vals['product_uom'][0]
                vals['flag_duplica']=False 
                vals['id']=False
                vals['gruppo']=vals['gruppo'][0]
                vals['bom_id']=vals['bom_id'][0]
                vals['product_id']=vals['product_id'][0]
                
                id_line = self.pool.get('mrp.bom.altern.comp').create(cr,uid,vals)
                self.pool.get('mrp.bom.altern.comp').write(cr,uid,[bom_line.id],{'flag_duplica':False})


        return {'type': 'ir.actions.act_window_close'}

duplica_line_bom()