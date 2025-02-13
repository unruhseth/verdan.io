from .models import Category, Item, Transaction
from app.extensions import db
from typing import Optional, Tuple, List, Dict, Any
from uuid import UUID


class InventoryService:
    """Service class for inventory business logic"""
    
    @staticmethod
    def get_tables(account_id: int) -> Dict[str, Any]:
        """Get the models for the inventory app"""
        return {
            'inventory_categories': Category,
            'inventory_items': Item,
            'inventory_transactions': Transaction
        }
    
    @staticmethod
    def create_item(account_id: int, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Create a new inventory item"""
        try:
            item = Item(account_id=account_id, **data)
            db.session.add(item)
            db.session.commit()
            return True, item.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def get_item(account_id: int, item_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific item"""
        item = Item.query.filter_by(id=item_id, account_id=account_id).first()
        return item.to_dict() if item else None

    @staticmethod
    def list_items(account_id: int) -> List[Dict[str, Any]]:
        """List all items for an account"""
        items = Item.query.filter_by(account_id=account_id).all()
        return [item.to_dict() for item in items]

    @staticmethod
    def update_item(account_id: int, item_id: str, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Update an item"""
        try:
            item = Item.query.filter_by(id=item_id, account_id=account_id).first()
            if not item:
                return False, {"error": "Item not found"}
            
            for key, value in data.items():
                setattr(item, key, value)
            
            db.session.commit()
            return True, item.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def delete_item(account_id: int, item_id: str) -> Tuple[bool, str]:
        """Delete an item"""
        try:
            item = Item.query.filter_by(id=item_id, account_id=account_id).first()
            if not item:
                return False, "Item not found"
            
            db.session.delete(item)
            db.session.commit()
            return True, "Item deleted successfully"
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def create_category(account_id: int, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Create a new category"""
        try:
            category = Category(account_id=account_id, **data)
            db.session.add(category)
            db.session.commit()
            return True, category.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def get_category_tree(account_id: int) -> List[Dict[str, Any]]:
        """Get category hierarchy"""
        categories = Category.query.filter_by(account_id=account_id).all()
        
        def build_tree(parent_id=None):
            nodes = []
            children = [c for c in categories if str(c.parent_id) == str(parent_id)]
            for child in children:
                node = child.to_dict()
                child_nodes = build_tree(child.id)
                if child_nodes:
                    node['children'] = child_nodes
                nodes.append(node)
            return nodes
        
        return build_tree()

    @staticmethod
    def update_item_quantity(
        account_id: int,
        item_id: UUID,
        quantity_change: int,
        transaction_type: str,
        reference: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """Update item quantity and create transaction record"""
        try:
            item = Item.query.filter_by(id=item_id, account_id=account_id).first()
            if not item:
                return False, {"error": "Item not found"}
            
            # Update quantity
            new_quantity = item.quantity + quantity_change
            if new_quantity < 0:
                return False, {"error": "Insufficient stock"}
            
            item.quantity = new_quantity
            
            # Create transaction record
            transaction = Transaction(
                account_id=account_id,
                item_id=item_id,
                transaction_type=transaction_type,
                quantity=quantity_change,
                reference=reference,
                notes=notes
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            return True, item.to_dict()
        except Exception as e:
            db.session.rollback()
            return False, {"error": str(e)}

    @staticmethod
    def get_low_stock_items(account_id: int) -> List[Dict[str, Any]]:
        """Get items that are at or below their reorder point"""
        items = Item.query.filter(
            (Item.account_id == account_id) &
            (Item.quantity <= Item.reorder_point)
        ).all()
        
        return [item.to_dict() for item in items]

    @staticmethod
    def get_item_transactions(
        account_id: int,
        item_id: UUID,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent transactions for an item"""
        transactions = Transaction.query.filter_by(
            account_id=account_id,
            item_id=item_id
        ).order_by(Transaction.created_at.desc()).limit(limit).all()
        
        return [txn.to_dict() for txn in transactions]

    @staticmethod
    def search_items(
        account_id: int,
        query: str = None,
        category_id: UUID = None,
        status: str = None
    ) -> List[Dict[str, Any]]:
        """Search inventory items with filters"""
        filters = [Item.account_id == account_id]
        
        if query:
            filters.append(
                (Item.name.ilike(f"%{query}%")) |
                (Item.sku.ilike(f"%{query}%")) |
                (Item.description.ilike(f"%{query}%"))
            )
        
        if category_id:
            filters.append(Item.category_id == category_id)
        
        items = Item.query.filter(*filters).all()
        return [item.to_dict() for item in items]
     