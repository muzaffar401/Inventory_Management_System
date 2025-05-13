import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
import json
import abc
from typing import Dict, List, Type

# Keep all your original OOP classes (Product, Electronics, Grocery, Clothing, Inventory) here
# ... [All your existing OOP classes remain unchanged] ...
# Custom Exceptions
class InventoryError(Exception):
    """Base exception for inventory-related errors"""
    pass

class InsufficientStockError(InventoryError):
    """Raised when trying to sell more items than available"""
    pass

class DuplicateProductError(InventoryError):
    """Raised when adding a product with a duplicate ID"""
    pass

class InvalidProductDataError(InventoryError):
    """Raised when loading invalid product data"""
    pass


# Abstract Base Class
class Product(abc.ABC):
    def __init__(self, product_id: str, name: str, price: float, quantity_in_stock: int):
        self._product_id = product_id
        self._name = name
        self._price = price
        self._quantity_in_stock = quantity_in_stock
    
    @property
    def product_id(self) -> str:
        return self._product_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def price(self) -> float:
        return self._price
    
    @price.setter
    def price(self, new_price: float):
        if new_price <= 0:
            raise ValueError("Price must be positive")
        self._price = new_price
    
    @property
    def quantity_in_stock(self) -> int:
        return self._quantity_in_stock
    
    def restock(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Restock amount must be positive")
        self._quantity_in_stock += amount
    
    def sell(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Sale quantity must be positive")
        if quantity > self._quantity_in_stock:
            raise InsufficientStockError(
                f"Not enough stock. Available: {self._quantity_in_stock}, Requested: {quantity}"
            )
        self._quantity_in_stock -= quantity
    
    def get_total_value(self) -> float:
        return self._price * self._quantity_in_stock
    
    @abc.abstractmethod
    def __str__(self) -> str:
        pass
    
    @abc.abstractmethod
    def to_dict(self) -> Dict:
        """Convert product to dictionary for serialization"""
        pass
    
    @classmethod
    @abc.abstractmethod
    def from_dict(cls, data: Dict) -> 'Product':
        """Create product from dictionary (deserialization)"""
        pass


# Product Subclasses
class Electronics(Product):
    def __init__(self, product_id: str, name: str, price: float, quantity_in_stock: int, 
                 warranty_years: int, brand: str):
        super().__init__(product_id, name, price, quantity_in_stock)
        self._warranty_years = warranty_years
        self._brand = brand
    
    @property
    def warranty_years(self) -> int:
        return self._warranty_years
    
    @property
    def brand(self) -> str:
        return self._brand
    
    def __str__(self) -> str:
        return (f"Electronics - ID: {self._product_id}, Name: {self._name}, "
                f"Brand: {self._brand}, Price: ${self._price:.2f}, "
                f"Warranty: {self._warranty_years} years, "
                f"Stock: {self._quantity_in_stock}")
    
    def to_dict(self) -> Dict:
        return {
            'type': 'electronics',
            'product_id': self._product_id,
            'name': self._name,
            'price': self._price,
            'quantity_in_stock': self._quantity_in_stock,
            'warranty_years': self._warranty_years,
            'brand': self._brand
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Electronics':
        return cls(
            data['product_id'],
            data['name'],
            data['price'],
            data['quantity_in_stock'],
            data['warranty_years'],
            data['brand']
        )


class Grocery(Product):
    def __init__(self, product_id: str, name: str, price: float, quantity_in_stock: int, 
                 expiry_date: str):
        super().__init__(product_id, name, price, quantity_in_stock)
        self._expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()
    
    @property
    def expiry_date(self) -> date:
        return self._expiry_date
    
    def is_expired(self) -> bool:
        return self._expiry_date < date.today()
    
    def __str__(self) -> str:
        expired = " (EXPIRED)" if self.is_expired() else ""
        return (f"Grocery - ID: {self._product_id}, Name: {self._name}, "
                f"Price: ${self._price:.2f}, Expiry: {self._expiry_date}{expired}, "
                f"Stock: {self._quantity_in_stock}")
    
    def to_dict(self) -> Dict:
        return {
            'type': 'grocery',
            'product_id': self._product_id,
            'name': self._name,
            'price': self._price,
            'quantity_in_stock': self._quantity_in_stock,
            'expiry_date': self._expiry_date.strftime("%Y-%m-%d")
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Grocery':
        return cls(
            data['product_id'],
            data['name'],
            data['price'],
            data['quantity_in_stock'],
            data['expiry_date']
        )


class Clothing(Product):
    def __init__(self, product_id: str, name: str, price: float, quantity_in_stock: int, 
                 size: str, material: str):
        super().__init__(product_id, name, price, quantity_in_stock)
        self._size = size
        self._material = material
    
    @property
    def size(self) -> str:
        return self._size
    
    @property
    def material(self) -> str:
        return self._material
    
    def __str__(self) -> str:
        return (f"Clothing - ID: {self._product_id}, Name: {self._name}, "
                f"Size: {self._size}, Material: {self._material}, "
                f"Price: ${self._price:.2f}, Stock: {self._quantity_in_stock}")
    
    def to_dict(self) -> Dict:
        return {
            'type': 'clothing',
            'product_id': self._product_id,
            'name': self._name,
            'price': self._price,
            'quantity_in_stock': self._quantity_in_stock,
            'size': self._size,
            'material': self._material
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Clothing':
        return cls(
            data['product_id'],
            data['name'],
            data['price'],
            data['quantity_in_stock'],
            data['size'],
            data['material']
        )


# Inventory Class
class Inventory:
    def __init__(self):
        self._products: Dict[str, Product] = {}
    
    def add_product(self, product: Product) -> None:
        if product.product_id in self._products:
            raise DuplicateProductError(f"Product ID {product.product_id} already exists")
        self._products[product.product_id] = product
    
    def remove_product(self, product_id: str) -> None:
        if product_id not in self._products:
            raise KeyError(f"Product ID {product_id} not found")
        del self._products[product_id]
    
    def search_by_name(self, name: str) -> List[Product]:
        return [p for p in self._products.values() if name.lower() in p.name.lower()]
    
    def search_by_type(self, product_type: Type[Product]) -> List[Product]:
        return [p for p in self._products.values() if isinstance(p, product_type)]
    
    def list_all_products(self) -> List[Product]:
        return list(self._products.values())
    
    def sell_product(self, product_id: str, quantity: int) -> None:
        if product_id not in self._products:
            raise KeyError(f"Product ID {product_id} not found")
        self._products[product_id].sell(quantity)
    
    def restock_product(self, product_id: str, quantity: int) -> None:
        if product_id not in self._products:
            raise KeyError(f"Product ID {product_id} not found")
        self._products[product_id].restock(quantity)
    
    def total_inventory_value(self) -> float:
        return sum(p.get_total_value() for p in self._products.values())
    
    def remove_expired_products(self) -> int:
        """Remove expired grocery items and return count of removed items"""
        to_remove = [
            pid for pid, p in self._products.items() 
            if isinstance(p, Grocery) and p.is_expired()
        ]
        for pid in to_remove:
            del self._products[pid]
        return len(to_remove)
    
    def save_to_file(self, filename: str) -> None:
        if not filename:
            raise ValueError("Filename cannot be empty")
        if not filename.endswith('.json'):
            filename += '.json'
        data = [p.to_dict() for p in self._products.values()]
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_file(self, filename: str) -> None:
        if not filename:
            raise ValueError("Filename cannot be empty")
        if not filename.endswith('.json'):
            filename += '.json'
            
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"File {filename} not found")
        except json.JSONDecodeError:
            raise InvalidProductDataError("Invalid JSON format in file")
        
        self._products = {}
        product_classes = {
            'electronics': Electronics,
            'grocery': Grocery,
            'clothing': Clothing
        }
        
        for item in data:
            try:
                product_type = item.get('type')
                if product_type not in product_classes:
                    raise InvalidProductDataError(f"Unknown product type: {product_type}")
                
                product_class = product_classes[product_type]
                product = product_class.from_dict(item)
                self.add_product(product)
            except (KeyError, ValueError) as e:
                raise InvalidProductDataError(f"Invalid product data: {e}")

class InventoryDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f2f5")
        
        self.inventory = Inventory()
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles
        self.style.configure('TFrame', background='#f0f2f5')
        self.style.configure('TLabel', background='#f0f2f5', font=('Segoe UI', 10))
        self.style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'))
        self.style.configure('TButton', font=('Segoe UI', 10), padding=6)
        self.style.configure('Primary.TButton', background='#4e73df', foreground='white')
        self.style.configure('Success.TButton', background='#1cc88a', foreground='white')
        self.style.configure('Danger.TButton', background='#e74a3b', foreground='white')
        self.style.configure('TEntry', padding=6)
        self.style.configure('TCombobox', padding=6)
        self.style.configure('Treeview', font=('Segoe UI', 10), rowheight=25)
        self.style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))
        self.style.map('Primary.TButton', background=[('active', '#3a5bc7')])
        self.style.map('Success.TButton', background=[('active', '#17a673')])
        self.style.map('Danger.TButton', background=[('active', '#d63a2b')])
        
        # Create main container
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.header_label = ttk.Label(
            self.header_frame, 
            text="Inventory Management System", 
            style='Header.TLabel'
        )
        self.header_label.pack(side=tk.LEFT)
        
        # Main content area
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        self.sidebar_frame = ttk.Frame(self.content_frame, width=200)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        # Main display area
        self.display_frame = ttk.Frame(self.content_frame)
        self.display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create sidebar buttons
        self.create_sidebar_buttons()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            root, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            font=('Segoe UI', 9)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.update_status("Ready")
        
        # Show dashboard by default
        self.show_dashboard()
    
    def update_status(self, message):
        """Update the status bar with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_var.set(f"{timestamp} - {message}")
    
    def create_sidebar_buttons(self):
        """Create navigation buttons in the sidebar"""
        buttons = [
            ("Dashboard", self.show_dashboard, 'Primary.TButton'),
            ("Add Product", self.show_add_product, 'Success.TButton'),
            ("View Products", self.show_view_products, None),
            ("Sell Product", self.show_sell_product, None),
            ("Restock", self.show_restock, None),
            ("Remove Expired", self.remove_expired, 'Danger.TButton'),
            ("Save/Load", self.show_save_load, None),
        ]
        
        for text, command, style in buttons:
            btn = ttk.Button(
                self.sidebar_frame,
                text=text,
                command=command,
                style=style,
                width=20
            )
            btn.pack(pady=5, fill=tk.X)
    
    def clear_display_frame(self):
        """Clear the display frame"""
        for widget in self.display_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        """Show the dashboard with summary information"""
        self.clear_display_frame()
        self.update_status("Viewing Dashboard")
        
        # Dashboard header
        header = ttk.Label(
            self.display_frame, 
            text="Dashboard Overview", 
            style='Header.TLabel'
        )
        header.pack(pady=(0, 20))
        
        # Summary cards frame
        cards_frame = ttk.Frame(self.display_frame)
        cards_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Create summary cards
        total_products = len(self.inventory.list_all_products())
        total_value = self.inventory.total_inventory_value()
        electronics = len(self.inventory.search_by_type(Electronics))
        groceries = len(self.inventory.search_by_type(Grocery))
        clothing = len(self.inventory.search_by_type(Clothing))
        
        cards = [
            ("Total Products", total_products, "#4e73df"),
            ("Inventory Value", f"${total_value:,.2f}", "#1cc88a"),
            ("Electronics", electronics, "#36b9cc"),
            ("Groceries", groceries, "#f6c23e"),
            ("Clothing", clothing, "#e74a3b"),
        ]
        
        for text, value, color in cards:
            card = ttk.Frame(cards_frame, relief=tk.RAISED, borderwidth=1)
            card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
            
            # Card header
            header = ttk.Label(
                card, 
                text=text, 
                foreground="white", 
                background=color,
                font=('Segoe UI', 10, 'bold'),
                padding=10
            )
            header.pack(fill=tk.X)
            
            # Card value
            value_label = ttk.Label(
                card, 
                text=value, 
                font=('Segoe UI', 14, 'bold'),
                padding=10
            )
            value_label.pack()
        
        # Recent products table
        recent_frame = ttk.Frame(self.display_frame)
        recent_frame.pack(fill=tk.BOTH, expand=True)
        
        recent_label = ttk.Label(
            recent_frame, 
            text="Recent Products", 
            font=('Segoe UI', 12, 'bold')
        )
        recent_label.pack(anchor=tk.W, pady=(10, 5))
        
        columns = ("ID", "Name", "Type", "Price", "Stock")
        self.recent_tree = ttk.Treeview(
            recent_frame, 
            columns=columns, 
            show="headings",
            selectmode="browse"
        )
        
        for col in columns:
            self.recent_tree.heading(col, text=col)
            self.recent_tree.column(col, width=120, anchor=tk.CENTER)
        
        self.recent_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add sample data (replace with actual data from inventory)
        products = self.inventory.list_all_products()[:10]  # Show up to 10 recent
        for product in products:
            product_type = "Electronics" if isinstance(product, Electronics) else \
                          "Grocery" if isinstance(product, Grocery) else "Clothing"
            self.recent_tree.insert("", tk.END, values=(
                product.product_id,
                product.name,
                product_type,
                f"${product.price:.2f}",
                product.quantity_in_stock
            ))
    
    def show_add_product(self):
        """Show the add product form"""
        self.clear_display_frame()
        self.update_status("Adding New Product")
        
        # Form header
        header = ttk.Label(
            self.display_frame, 
            text="Add New Product", 
            style='Header.TLabel'
        )
        header.pack(pady=(0, 20))
        
        # Form frame
        form_frame = ttk.Frame(self.display_frame)
        form_frame.pack(fill=tk.X)
        
        # Product type selection
        ttk.Label(form_frame, text="Product Type:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.product_type_var = tk.StringVar()
        type_combobox = ttk.Combobox(
            form_frame, 
            textvariable=self.product_type_var,
            values=["Electronics", "Grocery", "Clothing"],
            state="readonly"
        )
        type_combobox.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=5)
        type_combobox.current(0)
        type_combobox.bind("<<ComboboxSelected>>", self.update_product_form)
        
        # Common fields frame
        self.common_fields_frame = ttk.Frame(form_frame)
        self.common_fields_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW)
        
        # Product-specific fields frame
        self.specific_fields_frame = ttk.Frame(form_frame)
        self.specific_fields_frame.grid(row=2, column=0, columnspan=2, sticky=tk.EW)
        
        # Create common fields
        self.create_common_fields()
        
        # Create initial specific fields (for Electronics)
        self.create_specific_fields("Electronics")
        
        # Submit button
        submit_btn = ttk.Button(
            form_frame,
            text="Add Product",
            style='Success.TButton',
            command=self.add_product_submit
        )
        submit_btn.grid(row=3, column=1, sticky=tk.E, pady=10)
    
    def create_common_fields(self):
        """Create fields common to all product types"""
        # Clear the frame first
        for widget in self.common_fields_frame.winfo_children():
            widget.destroy()
        
        # Product ID
        ttk.Label(self.common_fields_frame, text="Product ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.product_id_entry = ttk.Entry(self.common_fields_frame)
        self.product_id_entry.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=5)
        
        # Name
        ttk.Label(self.common_fields_frame, text="Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(self.common_fields_frame)
        self.name_entry.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=5)
        
        # Price
        ttk.Label(self.common_fields_frame, text="Price:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.price_entry = ttk.Entry(self.common_fields_frame)
        self.price_entry.grid(row=2, column=1, sticky=tk.EW, pady=5, padx=5)
        
        # Quantity
        ttk.Label(self.common_fields_frame, text="Initial Quantity:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.quantity_entry = ttk.Entry(self.common_fields_frame)
        self.quantity_entry.grid(row=3, column=1, sticky=tk.EW, pady=5, padx=5)
        
        # Configure grid weights
        self.common_fields_frame.columnconfigure(1, weight=1)
    
    def create_specific_fields(self, product_type):
        """Create fields specific to the product type"""
        # Clear the frame first
        for widget in self.specific_fields_frame.winfo_children():
            widget.destroy()
        
        if product_type == "Electronics":
            # Warranty
            ttk.Label(self.specific_fields_frame, text="Warranty (years):").grid(row=0, column=0, sticky=tk.W, pady=5)
            self.warranty_entry = ttk.Entry(self.specific_fields_frame)
            self.warranty_entry.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=5)
            
            # Brand
            ttk.Label(self.specific_fields_frame, text="Brand:").grid(row=1, column=0, sticky=tk.W, pady=5)
            self.brand_entry = ttk.Entry(self.specific_fields_frame)
            self.brand_entry.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=5)
        
        elif product_type == "Grocery":
            # Expiry date
            ttk.Label(self.specific_fields_frame, text="Expiry Date (YYYY-MM-DD):").grid(row=0, column=0, sticky=tk.W, pady=5)
            self.expiry_entry = ttk.Entry(self.specific_fields_frame)
            self.expiry_entry.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=5)
        
        elif product_type == "Clothing":
            # Size
            ttk.Label(self.specific_fields_frame, text="Size:").grid(row=0, column=0, sticky=tk.W, pady=5)
            self.size_entry = ttk.Entry(self.specific_fields_frame)
            self.size_entry.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=5)
            
            # Material
            ttk.Label(self.specific_fields_frame, text="Material:").grid(row=1, column=0, sticky=tk.W, pady=5)
            self.material_entry = ttk.Entry(self.specific_fields_frame)
            self.material_entry.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=5)
        
        # Configure grid weights
        self.specific_fields_frame.columnconfigure(1, weight=1)
    
    def update_product_form(self, event=None):
        """Update the form when product type changes"""
        product_type = self.product_type_var.get()
        self.create_specific_fields(product_type)
    
    def add_product_submit(self):
        """Handle form submission for adding a new product"""
        try:
            # Get common fields
            product_id = self.product_id_entry.get()
            name = self.name_entry.get()
            price = float(self.price_entry.get())
            quantity = int(self.quantity_entry.get())
            
            # Validate required fields
            if not all([product_id, name]):
                raise ValueError("Product ID and Name are required")
            if price <= 0:
                raise ValueError("Price must be positive")
            if quantity < 0:
                raise ValueError("Quantity cannot be negative")
            
            # Create product based on type
            product_type = self.product_type_var.get()
            
            if product_type == "Electronics":
                warranty = int(self.warranty_entry.get())
                brand = self.brand_entry.get()
                if warranty < 0:
                    raise ValueError("Warranty years cannot be negative")
                if not brand:
                    raise ValueError("Brand is required")
                
                product = Electronics(product_id, name, price, quantity, warranty, brand)
            
            elif product_type == "Grocery":
                expiry = self.expiry_entry.get()
                try:
                    datetime.strptime(expiry, "%Y-%m-%d")
                except ValueError:
                    raise ValueError("Invalid date format. Use YYYY-MM-DD")
                
                product = Grocery(product_id, name, price, quantity, expiry)
            
            elif product_type == "Clothing":
                size = self.size_entry.get()
                material = self.material_entry.get()
                if not size:
                    raise ValueError("Size is required")
                if not material:
                    raise ValueError("Material is required")
                
                product = Clothing(product_id, name, price, quantity, size, material)
            
            # Add to inventory
            self.inventory.add_product(product)
            messagebox.showinfo("Success", "Product added successfully!")
            self.show_dashboard()
            self.update_status(f"Added product: {product_id} - {name}")
        
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except DuplicateProductError as e:
            messagebox.showerror("Duplicate Product", str(e))
    
    def show_view_products(self):
        """Show all products in a table view"""
        self.clear_display_frame()
        self.update_status("Viewing All Products")
        
        # Header
        header = ttk.Label(
            self.display_frame, 
            text="Product Inventory", 
            style='Header.TLabel'
        )
        header.pack(pady=(0, 20))
        
        # Filter controls
        filter_frame = ttk.Frame(self.display_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filter by:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.filter_var = tk.StringVar()
        filter_combobox = ttk.Combobox(
            filter_frame, 
            textvariable=self.filter_var,
            values=["All", "Electronics", "Grocery", "Clothing"],
            state="readonly",
            width=15
        )
        filter_combobox.pack(side=tk.LEFT)
        filter_combobox.current(0)
        filter_combobox.bind("<<ComboboxSelected>>", self.update_products_table)
        
        # Table frame
        table_frame = ttk.Frame(self.display_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview with scrollbars
        self.tree_scroll_y = ttk.Scrollbar(table_frame)
        self.tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree_scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        self.tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        columns = ("ID", "Name", "Type", "Price", "Stock", "Details")
        self.products_tree = ttk.Treeview(
            table_frame, 
            columns=columns, 
            show="headings",
            selectmode="browse",
            yscrollcommand=self.tree_scroll_y.set,
            xscrollcommand=self.tree_scroll_x.set
        )
        self.products_tree.pack(fill=tk.BOTH, expand=True)
        
        self.tree_scroll_y.config(command=self.products_tree.yview)
        self.tree_scroll_x.config(command=self.products_tree.xview)
        
        # Configure columns
        col_widths = [120, 200, 100, 80, 60, 200]
        for col, width in zip(columns, col_widths):
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=width, anchor=tk.CENTER)
        
        # Add data
        self.update_products_table()
    
    def update_products_table(self, event=None):
        """Update the products table based on filter"""
        filter_type = self.filter_var.get()
        
        if filter_type == "All":
            products = self.inventory.list_all_products()
        elif filter_type == "Electronics":
            products = self.inventory.search_by_type(Electronics)
        elif filter_type == "Grocery":
            products = self.inventory.search_by_type(Grocery)
        elif filter_type == "Clothing":
            products = self.inventory.search_by_type(Clothing)
        
        # Clear existing data
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # Add products to table
        for product in products:
            product_type = "Electronics" if isinstance(product, Electronics) else \
                          "Grocery" if isinstance(product, Grocery) else "Clothing"
            
            details = ""
            if isinstance(product, Electronics):
                details = f"Brand: {product.brand}, Warranty: {product.warranty_years} yrs"
            elif isinstance(product, Grocery):
                expired = " (EXPIRED)" if product.is_expired() else ""
                details = f"Expires: {product.expiry_date}{expired}"
            elif isinstance(product, Clothing):
                details = f"Size: {product.size}, Material: {product.material}"
            
            self.products_tree.insert("", tk.END, values=(
                product.product_id,
                product.name,
                product_type,
                f"${product.price:.2f}",
                product.quantity_in_stock,
                details
            ))
    
    def show_sell_product(self):
        """Show the sell product form"""
        self.clear_display_frame()
        self.update_status("Selling Product")
        
        # Header
        header = ttk.Label(
            self.display_frame, 
            text="Sell Product", 
            style='Header.TLabel'
        )
        header.pack(pady=(0, 20))
        
        # Check if inventory is empty
        if not self.inventory.list_all_products():
            ttk.Label(
                self.display_frame, 
                text="No products available to sell.", 
                font=('Segoe UI', 10, 'italic')
            ).pack()
            return
        
        # Form frame
        form_frame = ttk.Frame(self.display_frame)
        form_frame.pack(fill=tk.X)
        
        # Product selection
        ttk.Label(form_frame, text="Product ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.sell_product_id_var = tk.StringVar()
        product_combobox = ttk.Combobox(
            form_frame, 
            textvariable=self.sell_product_id_var,
            values=[p.product_id for p in self.inventory.list_all_products()],
            state="normal"
        )
        product_combobox.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=5)
        
        # Quantity
        ttk.Label(form_frame, text="Quantity:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.sell_quantity_entry = ttk.Entry(form_frame)
        self.sell_quantity_entry.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=5)
        
        # Submit button
        submit_btn = ttk.Button(
            form_frame,
            text="Sell Product",
            style='Primary.TButton',
            command=self.sell_product_submit
        )
        submit_btn.grid(row=2, column=1, sticky=tk.E, pady=10)
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)
    
    def sell_product_submit(self):
        """Handle product sale submission"""
        try:
            product_id = self.sell_product_id_var.get()
            quantity = int(self.sell_quantity_entry.get())
            
            if not product_id:
                raise ValueError("Please select a product")
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            
            self.inventory.sell_product(product_id, quantity)
            messagebox.showinfo("Success", "Product sold successfully!")
            self.show_dashboard()
            self.update_status(f"Sold {quantity} of product {product_id}")
        
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except InsufficientStockError as e:
            messagebox.showerror("Stock Error", str(e))
        except KeyError:
            messagebox.showerror("Error", "Product not found")
    
    def show_restock(self):
        """Show the restock form"""
        self.clear_display_frame()
        self.update_status("Restocking Product")
        
        # Header
        header = ttk.Label(
            self.display_frame, 
            text="Restock Product", 
            style='Header.TLabel'
        )
        header.pack(pady=(0, 20))
        
        # Check if inventory is empty
        if not self.inventory.list_all_products():
            ttk.Label(
                self.display_frame, 
                text="No products available to restock.", 
                font=('Segoe UI', 10, 'italic')
            ).pack()
            return
        
        # Form frame
        form_frame = ttk.Frame(self.display_frame)
        form_frame.pack(fill=tk.X)
        
        # Product selection
        ttk.Label(form_frame, text="Product ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.restock_product_id_var = tk.StringVar()
        product_combobox = ttk.Combobox(
            form_frame, 
            textvariable=self.restock_product_id_var,
            values=[p.product_id for p in self.inventory.list_all_products()],
            state="normal"
        )
        product_combobox.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=5)
        
        # Quantity
        ttk.Label(form_frame, text="Quantity to Add:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.restock_quantity_entry = ttk.Entry(form_frame)
        self.restock_quantity_entry.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=5)
        
        # Submit button
        submit_btn = ttk.Button(
            form_frame,
            text="Restock Product",
            style='Success.TButton',
            command=self.restock_product_submit
        )
        submit_btn.grid(row=2, column=1, sticky=tk.E, pady=10)
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)
    
    def restock_product_submit(self):
        """Handle restock submission"""
        try:
            product_id = self.restock_product_id_var.get()
            quantity = int(self.restock_quantity_entry.get())
            
            if not product_id:
                raise ValueError("Please select a product")
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            
            self.inventory.restock_product(product_id, quantity)
            messagebox.showinfo("Success", "Product restocked successfully!")
            self.show_dashboard()
            self.update_status(f"Restocked {quantity} of product {product_id}")
        
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except KeyError:
            messagebox.showerror("Error", "Product not found")
    
    def remove_expired(self):
        """Remove expired grocery items"""
        try:
            count = self.inventory.remove_expired_products()
            messagebox.showinfo("Success", f"Removed {count} expired grocery items")
            self.show_dashboard()
            self.update_status(f"Removed {count} expired grocery items")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def show_save_load(self):
        """Show save/load options"""
        self.clear_display_frame()
        self.update_status("Save/Load Inventory")
        
        # Header
        header = ttk.Label(
            self.display_frame, 
            text="Save/Load Inventory", 
            style='Header.TLabel'
        )
        header.pack(pady=(0, 20))
        
        # Save frame
        save_frame = ttk.LabelFrame(self.display_frame, text="Save Inventory", padding=10)
        save_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(save_frame, text="Save inventory to JSON file:").pack(anchor=tk.W)
        
        save_btn = ttk.Button(
            save_frame,
            text="Save Inventory",
            style='Primary.TButton',
            command=self.save_inventory
        )
        save_btn.pack(pady=5)
        
        # Load frame
        load_frame = ttk.LabelFrame(self.display_frame, text="Load Inventory", padding=10)
        load_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(load_frame, text="Load inventory from JSON file:").pack(anchor=tk.W)
        
        load_btn = ttk.Button(
            load_frame,
            text="Load Inventory",
            style='Success.TButton',
            command=self.load_inventory
        )
        load_btn.pack(pady=5)
    
    def save_inventory(self):
        """Save inventory to file"""
        if not self.inventory.list_all_products():
            messagebox.showwarning("Warning", "No products to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Save Inventory As"
        )
        
        if file_path:
            try:
                self.inventory.save_to_file(file_path)
                messagebox.showinfo("Success", "Inventory saved successfully!")
                self.update_status(f"Inventory saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save inventory: {str(e)}")
    
    def load_inventory(self):
        """Load inventory from file"""
        # Confirm if user wants to overwrite current inventory
        if self.inventory.list_all_products():
            if not messagebox.askyesno(
                "Confirm", 
                "Loading will replace current inventory. Continue?"
            ):
                return
        
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            title="Select Inventory File"
        )
        
        if file_path:
            try:
                self.inventory.load_from_file(file_path)
                messagebox.showinfo("Success", "Inventory loaded successfully!")
                self.show_dashboard()
                self.update_status(f"Inventory loaded from {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load inventory: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryDashboard(root)
    root.mainloop()