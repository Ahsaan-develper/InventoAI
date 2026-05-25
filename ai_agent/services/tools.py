from store.models import Item

class ProductTools:
    """Tools for the AI agent to interact with the database"""
    
    @staticmethod
    def search_products(query: str) -> list:
        """Search products by name or description"""
        items = Item.objects.filter(
            title__icontains=query
        ) | Item.objects.filter(
            description__icontains=query
        )
        return [
            {
                "id": item.id,
                "title": item.title,
                "description": item.description,
                "price": float(item.price),
                "quantity": getattr(item, 'quantity', 0),  # ADDED
                "image": item.image
            }
            for item in items[:5]
        ]
    
    @staticmethod
    def get_product_details(product_id: int) -> dict:
        """Get full details of a specific product"""
        try:
            item = Item.objects.get(id=product_id)
            qty = getattr(item, 'quantity', 0)
            return {
                "id": item.id,
                "title": item.title,
                "description": item.description,
                "price": float(item.price),
                "quantity": qty,  # ADDED
                "image": item.image,
                "available": qty > 0  # Dynamic stock check
            }
        except Item.DoesNotExist:
            return {"error": "Product not found"}
    
    @staticmethod
    def get_all_products() -> list:
        """Get all available products"""
        items = Item.objects.all()
        return [
            {
                "id": item.id,
                "title": item.title,
                "price": float(item.price),
                "quantity": getattr(item, 'quantity', 0)  # ADDED
            }
            for item in items
        ]
    
    @staticmethod
    def get_price_range(min_price: float = 0, max_price: float = 999999) -> list:
        """Get products within a price range"""
        items = Item.objects.filter(price__gte=min_price, price__lte=max_price)
        return [
            {
                "id": item.id,
                "title": item.title,
                "price": float(item.price),
                "quantity": getattr(item, 'quantity', 0)  # ADDED
            }
            for item in items
        ]

from store.models import Item

class ProductTools:
    """Tools for the AI agent to interact with the database"""
    
    @staticmethod
    def search_products(query: str) -> list:
        """Search products by name or description"""
        items = Item.objects.filter(
            title__icontains=query
        ) | Item.objects.filter(
            description__icontains=query
        )
        return [
            {
                "id": item.id,
                "title": item.title,
                "description": item.description,
                "price": float(item.price),
                "quantity": getattr(item, 'quantity', 0),
                "image": item.image
            }
            for item in items[:5]
        ]
    
    @staticmethod
    def get_product_details(product_id: int) -> dict:
        """Get full details of a specific product"""
        try:
            item = Item.objects.get(id=product_id)
            qty = getattr(item, 'quantity', 0)
            unit_price = float(item.price)
            total_value = unit_price * qty  # ADDED: Total inventory value
            
            return {
                "id": item.id,
                "title": item.title,
                "description": item.description,
                "price": unit_price,
                "quantity": qty,
                "total_value": total_value,  # ADDED
                "image": item.image,
                "available": qty > 0
            }
        except Item.DoesNotExist:
            return {"error": "Product not found"}
    
    @staticmethod
    def get_all_products() -> list:
        """Get all available products"""
        items = Item.objects.all()
        return [
            {
                "id": item.id,
                "title": item.title,
                "price": float(item.price),
                "quantity": getattr(item, 'quantity', 0)
            }
            for item in items
        ]
    
    @staticmethod
    def get_price_range(min_price: float = 0, max_price: float = 999999) -> list:
        """Get products within a price range"""
        items = Item.objects.filter(price__gte=min_price, price__lte=max_price)
        return [
            {
                "id": item.id,
                "title": item.title,
                "price": float(item.price),
                "quantity": getattr(item, 'quantity', 0)
            }
            for item in items
        ]
    
    # ====== NEW TOOLS ADDED ======
    
    @staticmethod
    def get_total_products_count() -> dict:
        """Get total number of products in inventory"""
        total = Item.objects.count()
        in_stock = Item.objects.filter(quantity__gt=0).count()
        out_of_stock = Item.objects.filter(quantity=0).count()
        
        return {
            "total_products": total,
            "in_stock": in_stock,
            "out_of_stock": out_of_stock
        }
    
    @staticmethod
    def get_product_total_value(product_name: str) -> dict:
        """Calculate total value of a product (price × quantity)"""
        items = Item.objects.filter(title__icontains=product_name)
        
        if not items.exists():
            return {"error": f"No product found with name '{product_name}'"}
        
        results = []
        for item in items:
            qty = getattr(item, 'quantity', 0)
            unit_price = float(item.price)
            total_value = unit_price * qty
            
            results.append({
                "id": item.id,
                "title": item.title,
                "unit_price": unit_price,
                "quantity": qty,
                "total_value": total_value,
                "calculation": f"${unit_price} × {qty} = ${total_value}"
            })
        
        return {
            "products_found": len(results),
            "results": results
        }