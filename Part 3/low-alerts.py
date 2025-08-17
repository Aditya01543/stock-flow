@app.route('/api/companies/<int:company_id>/alerts/low-stock', methods=['GET'])

def low_stock_alerts(company_id):
    
    alerts = []

    try:
        results = db.session.query(
            Product.id, Product.name, Product.sku,
            Warehouse.id.label("warehouse_id"), Warehouse.name.label("warehouse_name"),
            Inventory.quantity, Product.low_stock_threshold,
            Supplier.id.label("supplier_id"), Supplier.name.label("supplier_name"), Supplier.contact_email
        ).join(Inventory, Inventory.product_id == Product.id) \
        .join(Warehouse, Warehouse.id == Inventory.warehouse_id) \
        .join(SupplierProduct, SupplierProduct.product_id == Product.id) \
        .join(Supplier, Supplier.id == SupplierProduct.supplier_id) \
        .filter(Warehouse.company_id == company_id, Inventory.quantity < Product.low_stock_threshold) \
        .all()

        for r in results:
            days_until_stockout = estimate_stockout_days(r.id, r.warehouse_id)
            alerts.append({
                "product_id": r.id,
                "product_name": r.name,
                "sku": r.sku,
                "warehouse_id": r.warehouse_id,
                "warehouse_name": r.warehouse_name,
                "current_stock": r.quantity,
                "threshold": r.low_stock_threshold,
                "days_until_stockout": days_until_stockout,
                "supplier": {
                    "id": r.supplier_id,
                    "name": r.supplier_name,
                    "contact_email": r.contact_email
                }
            })
        
        return {"alerts": alerts, "total_alerts": len(alerts)}, 200
    
    except Exception as e:
        return {"error": str(e)}, 500