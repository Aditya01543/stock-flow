@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.json

    requiredFields = ["name", "sku", "price", "warehouse_id", "initial_quantity"]
    for field in requiredFields:
        if field not in data:
            return {"error" : f"{field} is missing"}, 400
    
    if Product.query.filter_by(sku=data['sku']).first():
        return {"error" : f"SKU must be unique"}, 400
    
    try:
        # Create new product
        product = Product(
            name=data['name'],
            sku=data['sku'],
            price=Decimal(str(data['price'])),
            warehouse_id=data['warehouse_id']
        )
        db.session.add(product)
        db.session.flush()

        # Update inventory count
        inventory = Inventory(
            product_id=product.id,
            warehouse_id=data['warehouse_id'],
            quantity=data.get('initial_quantity', 0)
        )
        db.session.add(inventory)

        db.session.commit()
        return {"message": "Product created", "product_id": product.id}
    
    except Exception as e:
        db.session.rollback()
        return {"error" : str(e)}, 500