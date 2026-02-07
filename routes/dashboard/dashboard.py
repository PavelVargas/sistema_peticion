import os
import pandas as pd
from flask import Blueprint, render_template, session, redirect, request, url_for, current_app, jsonify
from werkzeug.utils import secure_filename
from models.User.user import User
from models.peticion.peticion import Peticion, Producto ,PeticionProducto
from db import db

dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    user_id = session.get('user_id')
    if not user_id: return redirect(url_for('login_bp.login'))
    user = User.query.get(user_id)

    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        archivo = request.files.get('archivo')
        
        nombre_archivo = None
        if archivo and archivo.filename != '':
            nombre_archivo = secure_filename(archivo.filename)
            archivo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], nombre_archivo))
        
        nueva_peticion = Peticion(
            titulo=titulo, 
            descripcion=descripcion, 
            user_id=user.id, 
            archivo_adjunto=nombre_archivo
        )
        db.session.add(nueva_peticion)
        db.session.flush()

        # Captura de productos
        productos_ids = request.form.getlist('productos_ids')
        for p_id in productos_ids:
            cant = request.form.get(f'cant_{p_id}')
            if cant and int(cant) > 0:
                detalle = PeticionProducto(
                    peticion_id=nueva_peticion.id,
                    producto_id=int(p_id),
                    cantidad_solicitada=int(cant)
                )
                db.session.add(detalle)
        
        db.session.commit()
        return redirect(url_for('dashboard_bp.dashboard'))

    # Lógica de renderizado
    peticiones = Peticion.query.filter_by(user_id=user.id).order_by(Peticion.fecha_creacion.desc()).all()
    productos_stock = Producto.query.filter(Producto.cantidad > 0).all()
    
    # DETECTAR SI ES AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    return render_template('dashboard/dashboard.html', 
                           user=user, 
                           peticiones=peticiones, 
                           productos_stock=productos_stock, 
                           is_ajax=is_ajax)

@dashboard_bp.route('/admin')
def admin_panel():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or not user.is_admin: return "Acceso denegado", 403

    sucursal_filtro = request.args.get('sucursal', 'Todas')
    from sqlalchemy.orm import joinedload
    
    query = Peticion.query.join(User)
    if sucursal_filtro != 'Todas':
        query = query.filter(User.sucursal == sucursal_filtro)
    
    all_peticiones = query.options(
        joinedload(Peticion.user),
        joinedload(Peticion.productos_solicitados).joinedload(PeticionProducto.producto)
    ).order_by(Peticion.fecha_creacion.desc()).all()

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    return render_template('admin/admin.html', peticiones=all_peticiones, current_filter=sucursal_filtro, is_ajax=is_ajax)
@dashboard_bp.route('/admin/inventario')
def admin_inventario():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or not user.is_admin: 
        return "Acceso denegado", 403

    # --- AGREGAR ESTA LÍNEA PARA DETECTAR AJAX ---
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    filtro_vista = request.args.get('vista', 'stock') 
    
    productos_base = Producto.query.order_by(Producto.nombre.asc()).all()
    categorias = db.session.query(Producto.categoria).distinct().all()
    lista_categorias = [c[0] for c in categorias if c[0]]

    productos_finales = []

    if filtro_vista == 'salidos':
        salidas_map = {}
        peticiones_enviadas = Peticion.query.filter_by(estado='Enviado').all()
        
        for p in peticiones_enviadas:
            for item in p.productos_solicitados:
                pid = item.producto_id
                salidas_map[pid] = salidas_map.get(pid, 0) + item.cantidad_solicitada
        
        for p in productos_base:
            if p.id in salidas_map:
                productos_finales.append({
                    'id': p.id,
                    'nombre': p.nombre,
                    'categoria': p.categoria,
                    'cantidad': salidas_map[p.id], 
                    'es_salida': True
                })
    else:
        for p in productos_base:
            productos_finales.append({
                'id': p.id,
                'nombre': p.nombre,
                'categoria': p.categoria,
                'cantidad': p.cantidad,
                'es_salida': False
            })

    return render_template('admin/inventario.html', 
                           productos=productos_finales, 
                           categorias=lista_categorias,
                           vista=filtro_vista,
                           is_ajax=is_ajax)

@dashboard_bp.route('/admin/subir_stock', methods=['POST'])
def subir_stock():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or not user.is_admin: return redirect(url_for('login_bp.login'))

    archivo = request.files.get('excel_stock')
    if archivo and archivo.filename != '':
        try:
            df = pd.read_excel(archivo)
            df.columns = [str(c).strip().capitalize() for c in df.columns]

            for _, row in df.iterrows():
                if 'Producto' not in df.columns or 'Cantidad' not in df.columns: continue
                
                nombre_raw = str(row['Producto']).strip()
                if not nombre_raw or nombre_raw.lower() == 'nan': continue

                try:
                    cantidad_val = int(row['Cantidad'])
                except:
                    cantidad_val = 0
                
                cat_val = str(row.get('Categoria', 'General')).strip()
                if cat_val.lower() == 'nan': cat_val = 'General'

                prod = Producto.query.filter_by(nombre=nombre_raw).first()
                if prod:
                    prod.cantidad = cantidad_val
                    prod.categoria = cat_val
                else:
                    db.session.add(Producto(nombre=nombre_raw, cantidad=cantidad_val, categoria=cat_val))
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error en Excel: {e}")

    return redirect(url_for('dashboard_bp.admin_inventario'))

# --- ACTUALIZADO: RUTA PARA DESCONTAR CANTIDAD VARIABLE ---
@dashboard_bp.route('/admin/descontar/<int:id>', methods=['POST'])
def descontar_stock(id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or not user.is_admin: return jsonify({"error": "No autorizado"}), 403

    producto = Producto.query.get_or_404(id)
    data = request.get_json()
    cantidad_a_quitar = int(data.get('cantidad', 1))

    if producto.cantidad >= cantidad_a_quitar:
        producto.cantidad -= cantidad_a_quitar
        db.session.commit()
        return jsonify({"success": True, "nueva_cantidad": producto.cantidad})
    
    return jsonify({"error": "Stock insuficiente"}), 400

@dashboard_bp.route('/admin/cambiar_estado/<int:id>', methods=['POST'])
def cambiar_estado(id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or not user.is_admin: 
        return jsonify({"error": "No autorizado"}), 403

    peticion = Peticion.query.get_or_404(id)
    nuevo_estado = request.json.get('estado')
    
    if nuevo_estado not in ['Pendiente', 'Preparando', 'Enviado']:
        return jsonify({"error": "Estado inválido"}), 400

    if nuevo_estado == 'Enviado' and peticion.estado != 'Enviado':

        for item in peticion.productos_solicitados:
            if item.producto.cantidad < item.cantidad_solicitada:
                return jsonify({
                    "error": f"Stock insuficiente para {item.producto.nombre}. Disponible: {item.producto.cantidad}"
                }), 400

        for item in peticion.productos_solicitados:
            item.producto.cantidad -= item.cantidad_solicitada
    
    peticion.estado = nuevo_estado
    try:
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@dashboard_bp.route('/admin/limpiar_inventario', methods=['POST'])
def limpiar_inventario():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({"error": "No autorizado"}), 403

    try:
        Producto.query.update({Producto.cantidad: 0})
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500