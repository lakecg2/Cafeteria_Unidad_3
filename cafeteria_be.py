import tkinter as tk
from uuid import uuid4
from tkinter import ttk, messagebox, simpledialog
from enum import Enum
from typing import List, Dict, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
import os
import csv

# -------------------- ENUMS -------------------- #
class RolEmpleado(Enum):
    MESERO = "mesero"
    BARISTA = "barista"
    GERENTE = "gerente"



class TipoBebida(Enum):
    CALIENTE = "caliente"
    FRIA = "fria"
    BATIDO = "batido"

# -------------------- CLASES BASE -------------------- #
@dataclass
class Persona:
    id: str
    nombre: str = ""
    telefono: str = ""
    email: str = ""

@dataclass
class Cliente(Persona):
    historial_pedidos: List['Pedido'] = field(default_factory=list)
    puntos_fidelidad: int = 0
    alergias: List[str] = field(default_factory=list)
    contrasena: str = field(default="123456", repr=False)

    def verificar_contrasena(self, contrasena_ingresada: str) -> bool:
        """Verifica la contraseña con trim y comparación exacta"""
        return self.contrasena.strip() == contrasena_ingresada.strip()

    def agregar_puntos(self, puntos: int):
        """Agrega puntos al cliente con validación"""
        if puntos > 0:  # Solo agregar puntos positivos
            self.puntos_fidelidad += puntos
            return True
        return False
        
    def canjear_puntos(self, puntos: int) -> bool:
        """Intenta canjear puntos, devuelve True si fue exitoso"""
        if puntos <= 0:
            raise ValueError("Debe canjear un número positivo de puntos")
        if self.puntos_fidelidad >= puntos:
            self.puntos_fidelidad -= puntos
            return True
        return False
    
@dataclass
class Empleado(Persona):
    id_empleado: str = ""
    rol: RolEmpleado = RolEmpleado.MESERO
    salario: float = 0.0
    activo: bool = True
    contrasena: str = field(default="123456", repr=False)
    puntos_fidelidad: int = 0  # Añadir este campo

    def verificar_contrasena(self, contrasena_ingresada: str) -> bool:
        return self.contrasena == contrasena_ingresada.strip()
    
    def agregar_puntos(self, puntos: int):
        """Agrega puntos al empleado con validación"""
        if puntos > 0:
            self.puntos_fidelidad += puntos
            return True
        return False
        
    def canjear_puntos(self, puntos: int) -> bool:
        """Intenta canjear puntos, devuelve True si fue exitoso"""
        if puntos <= 0:
            raise ValueError("Debe canjear un número positivo de puntos")
        if self.puntos_fidelidad >= puntos:
            self.puntos_fidelidad -= puntos
            return True
        return False
    


# -------------------- PRODUCTOS -------------------- #
@dataclass
class ProductoBase:
    nombre: str
    precio_base: float
    descripcion: str
    # Eliminado: tiempo_preparacion: int = 0

@dataclass
class Bebida(ProductoBase):
    tipo: TipoBebida
    ingredientes_base: Dict[str, int] = field(default_factory=dict)
    tamanos_disponibles: List[str] = field(default_factory=lambda: ["pequeño", "mediano", "grande"])
    tiempo_preparacion: int = 0
    precios_tamanos: Dict[str, float] = field(default_factory=dict)  # Nuevo campo para precios por tamaño

    def __post_init__(self):
        if not isinstance(self.tipo, TipoBebida):
            raise ValueError("El tipo de bebida debe ser una instancia de TipoBebida")
        
        # Inicializar precios por tamaño si no se especificaron
        if not self.precios_tamanos and self.tamanos_disponibles:
            # Precios base por defecto (puedes ajustarlos)
            precios_base = {
                "pequeño": self.precio_base * 0.8,
                "mediano": self.precio_base,
                "grande": self.precio_base * 1.2
            }
            self.precios_tamanos = {
                tamano: precios_base.get(tamano, self.precio_base)
                for tamano in self.tamanos_disponibles
            }

    def calcular_precio_tamano(self, tamano: str) -> float:
        """Calcula el precio según el tamaño seleccionado"""
        if tamano not in self.tamanos_disponibles:
            raise ValueError(f"Tamaño {tamano} no disponible")
        return self.precios_tamanos.get(tamano, self.precio_base)

@dataclass
class Postre(ProductoBase):
    es_vegano: bool = False
    sin_gluten: bool = False
    requiere_horneado: bool = False
    ingredientes_base: Dict[str, int] = field(default_factory=dict)
    tiempo_preparacion: int = 0  # Añadido aquí

    def etiquetas(self) -> List[str]:
        tags = []
        if self.es_vegano:
            tags.append("Vegano")
        if self.sin_gluten:
            tags.append("Sin gluten")
        if self.requiere_horneado:
            tags.append("Horneado")
        return tags

@dataclass
class ProductoPersonalizado:
    producto_base: ProductoBase
    precio_final: float = 0.0
    modificaciones: Dict[str, int] = field(default_factory=dict)
    notas: str = ""
    tamano: str = "mediano"

    def __post_init__(self):
        self.precio_final = self._calcular_precio_inicial()

    def _calcular_precio_inicial(self) -> float:
        """Calcula el precio inicial basado en el producto base"""
        if isinstance(self.producto_base, Bebida):
            return self.producto_base.calcular_precio_tamano(self.tamano)
        return self.producto_base.precio_base

    @property
    def nombre(self) -> str:
        nombre = self.producto_base.nombre
        if isinstance(self.producto_base, Bebida):
            nombre += f" ({self.tamano})"
        if self.modificaciones:
            mods = [f"extra {ing}" if cant > 0 else f"sin {ing}" 
                   for ing, cant in self.modificaciones.items()]
            nombre += f" ({', '.join(mods)})"
        if self.notas:
            nombre += f" [Nota: {self.notas}]"
        return nombre

# -------------------- INVENTARIO -------------------- #
@dataclass
class Inventario:
    stock: Dict[str, int] = field(default_factory=dict)
    proveedores: Dict[str, str] = field(default_factory=dict)
    umbral_reorden: Dict[str, int] = field(default_factory=dict)

    def agregar_ingrediente(self, ingrediente: str, cantidad: int, proveedor: str = "", umbral: int = 10) -> None:
        if ingrediente in self.stock:
            raise ValueError(f"El ingrediente {ingrediente} ya existe")
        self.stock[ingrediente] = cantidad
        if proveedor:
            self.proveedores[ingrediente] = proveedor
        self.umbral_reorden[ingrediente] = umbral

    def actualizar_cantidad(self, ingrediente: str, cantidad: int) -> None:
        if ingrediente not in self.stock:
            raise ValueError(f"Ingrediente {ingrediente} no encontrado")
        nuevo_stock = self.stock[ingrediente] + cantidad
        if nuevo_stock < 0:
            raise ValueError("No puede haber stock negativo")
        self.stock[ingrediente] = nuevo_stock

# -------------------- PEDIDOS -------------------- #
@dataclass
class Pedido:
    cliente: Cliente
    productos: List[ProductoPersonalizado]

    fecha_creacion: datetime = field(default_factory=datetime.now)
    total: float = field(init=False)
    puntos_obtenidos: int = field(init=False)
    id_pedido: str = field(default_factory=lambda: str(uuid4())[:8].upper())  # ID de 8 caracteres

    def __post_init__(self):
        self._calcular_total()
        self._calcular_puntos()

    def _calcular_total(self):
        self.total = round(sum(p.precio_final for p in self.productos), 2)

    def _calcular_puntos(self):
        self.puntos_obtenidos = int(self.total // 5)  # 1 punto por cada $5
        if hasattr(self.cliente, 'agregar_puntos'):
            self.cliente.agregar_puntos(self.puntos_obtenidos)
# -------------------- CAFETERÍA -------------------- #
@dataclass
class Promocion:
    nombre: str
    descuento_porcentaje: float
    codigo: str
    valido_desde: datetime
    valido_hasta: datetime
    activa: bool = True
    puntos_requeridos: int = 0
    productos_minimos: int = 0

    def es_aplicable(self, pedido: Pedido) -> bool:
        ahora = datetime.now()
        return (self.activa and 
                ahora >= self.valido_desde and 
                ahora <= self.valido_hasta and
                (self.puntos_requeridos == 0 or 
                 (hasattr(pedido.cliente, 'puntos_fidelidad') and 
                  pedido.cliente.puntos_fidelidad >= self.puntos_requeridos)) and
                (self.productos_minimos == 0 or 
                 len(pedido.productos) >= self.productos_minimos))

    def aplicar_descuento(self, total: float, cliente: Optional[Cliente] = None) -> float:
        """Aplica descuento y consume puntos si es necesario"""
        if self.puntos_requeridos > 0 and cliente:
            if not cliente.canjear_puntos(self.puntos_requeridos):
                raise ValueError("Puntos insuficientes para esta promoción")
        return total * (1 - self.descuento_porcentaje / 100)
    
@dataclass
class Cafeteria:
    nombre: str
    direccion: str
    telefono: str
    inventario: Inventario = field(default_factory=Inventario)
    menu: Dict[str, ProductoBase] = field(default_factory=dict)
    clientes: Dict[str, Cliente] = field(default_factory=dict)
    empleados: Dict[str, Empleado] = field(default_factory=dict)
    promociones: List[Promocion] = field(default_factory=list)


    def filtrar_productos(self, condicion: Callable[[ProductoBase], bool]) -> Dict[str, ProductoBase]:
        """Filtra los productos del menú según la condición dada"""
        return {nombre: producto for nombre, producto in self.menu.items() if condicion(producto)}
    

    def registrar_cliente(self, cliente: Cliente) -> None:
        """Registra un cliente y actualiza el CSV"""
        if cliente.id in self.clientes:
            raise ValueError(f"Cliente con ID {cliente.id} ya existe")
        if any(c.email.lower() == cliente.email.lower() for c in self.clientes.values()):
            raise ValueError(f"El email {cliente.email} ya está registrado")

        # Asegurarnos que la contraseña no tenga espacios
        cliente.contrasena = cliente.contrasena.strip()
        self.clientes[cliente.id] = cliente
        self.guardar_clientes_csv()

    def guardar_clientes_csv(self, archivo: str = 'clientes.csv') -> None:
        """Guarda clientes asegurando formato consistente"""
        try:
            with open(archivo, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Añadir encabezados actualizados
                writer.writerow(['nombre', 'id', 'telefono', 'email', 'contrasena', 'puntos_fidelidad', 'alergias'])
                for cliente in self.clientes.values():
                    writer.writerow([
                        cliente.nombre.strip(),
                        cliente.id.strip(),
                        cliente.telefono.strip(),
                        cliente.email.strip().lower(),
                        cliente.contrasena.strip(),
                        str(cliente.puntos_fidelidad),  # Guardar puntos
                        ','.join(cliente.alergias) if cliente.alergias else ''  # Guardar alergias como string separado por comas
                    ])
        except Exception as e:
            raise Exception(f"No se pudo guardar los clientes: {str(e)}")

    def cargar_clientes_csv(self, archivo: str = 'clientes.csv') -> None:
        """Carga clientes con normalización de datos"""
        try:
            if os.path.exists(archivo):
                with open(archivo, mode='r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        try:
                            cliente = Cliente(
                                nombre=row['nombre'].strip(),
                                id=row['id'].strip(),
                                telefono=row['telefono'].strip(),
                                email=row['email'].strip().lower(),
                                contrasena=row['contrasena'].strip()
                            )

                            # Cargar puntos de fidelidad si existen
                            if 'puntos_fidelidad' in row:
                                cliente.puntos_fidelidad = int(row['puntos_fidelidad'])

                            # Cargar alergias si existen
                            if 'alergias' in row and row['alergias'].strip():
                                cliente.alergias = [a.strip() for a in row['alergias'].split(',') if a.strip()]

                            self.clientes[cliente.id] = cliente
                        except KeyError as e:
                            print(f"Error en formato de fila: {row} - {str(e)}")
                            continue
        except Exception as e:
            raise Exception(f"No se pudo cargar los clientes: {str(e)}")
    
    def guardar_empleados_csv(self, archivo: str = 'empleados.csv') -> None:
        """Guarda empleados incluyendo puntos de fidelidad"""
        try:
            with open(archivo, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    'nombre', 'id', 'id_empleado', 'telefono', 'email', 
                    'contrasena', 'rol', 'salario', 'activo', 'puntos_fidelidad'
                ])

                for empleado in self.empleados.values():
                    id_empleado = empleado.id_empleado if empleado.id_empleado else empleado.id
                    writer.writerow([
                        empleado.nombre.strip(),
                        empleado.id.strip(),
                        id_empleado.strip(),
                        empleado.telefono.strip(),
                        empleado.email.strip().lower(),
                        empleado.contrasena.strip(),
                        empleado.rol.value.lower(),
                        str(float(empleado.salario)),
                        '1' if empleado.activo else '0',
                        str(empleado.puntos_fidelidad)  # Guardar puntos
                    ])
        except Exception as e:
            raise Exception(f"No se pudo guardar los empleados: {str(e)}")

    def cargar_empleados_csv(self, archivo: str = 'empleados.csv') -> None:
        """Carga empleados incluyendo puntos de fidelidad"""
        try:
            if os.path.exists(archivo):
                with open(archivo, mode='r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        try:
                            empleado = Empleado(
                                nombre=row['nombre'].strip(),
                                id=row['id'].strip(),
                                id_empleado=row['id_empleado'].strip(),
                                telefono=row['telefono'].strip(),
                                email=row['email'].strip().lower(),
                                contrasena=row['contrasena'].strip(),
                                rol=RolEmpleado(row['rol']),
                                salario=float(row['salario']),
                                activo=row['activo'] == '1'
                            )

                            # Cargar puntos si existen en el CSV
                            if 'puntos_fidelidad' in row:
                                empleado.puntos_fidelidad = int(row['puntos_fidelidad'])

                            self.empleados[empleado.id_empleado] = empleado
                        except KeyError as e:
                            print(f"Error en formato de fila: {row} - {str(e)}")
                            continue
        except Exception as e:
            raise Exception(f"No se pudo cargar los empleados: {str(e)}")
        
    def autenticar_usuario(self, usuario: str, contrasena: str) -> Optional[Persona]:
        """Autenticación mejorada con manejo de casos"""
        if not usuario or not contrasena:
            return None

        usuario = usuario.strip()
        contrasena = contrasena.strip()

        # Buscar cliente (comparar con email o ID, sin case sensitive)
        for cliente in self.clientes.values():
            if (cliente.email.lower() == usuario.lower() or 
                cliente.id.lower() == usuario.lower()):
                if cliente.verificar_contrasena(contrasena):
                    return cliente

           # Buscar empleado (comparar con email o ID_empleado, sin case sensitive)
            for empleado in self.empleados.values():
               if (empleado.email.lower() == usuario.lower() or 
                   empleado.id_empleado.lower() == usuario.lower()):
                   if empleado.verificar_contrasena(contrasena):
                       return empleado

            return None

    def inicializar_datos_prueba(self) -> None:
        """Datos de prueba completos con ingredientes y productos"""
        # Clientes de prueba
        clientes = [
            Cliente(nombre="Juan Pérez", id="C001", telefono="555-1001", email="juan@email.com", contrasena="123456"),
            Cliente(nombre="María García", id="C002", telefono="555-1002", email="maria@email.com", contrasena="123456")
        ]

        for cliente in clientes:
            self.clientes[cliente.id] = cliente

        # Guardar clientes
        self.guardar_clientes_csv()

        # Empleados de prueba
        empleados = [
            Empleado(nombre="Ana López", id="E001", rol=RolEmpleado.BARISTA, telefono="555-2001", 
                    email="ana@email.com", salario=1200, activo=True, contrasena="123456", puntos_fidelidad= 50),
            Empleado(nombre="Carlos Ruiz", id="E002", rol=RolEmpleado.MESERO, telefono="555-2002", 
                    email="carlos@email.com", salario=1000, activo=True, contrasena="123456", puntos_fidelidad= 50),
            Empleado(nombre="Luisa Martínez", id="E003", rol=RolEmpleado.GERENTE, telefono="555-2003", 
                    email="luisa@email.com", salario=2000, activo=True, contrasena="123456", puntos_fidelidad= 500),
        ]

        for empleado in empleados:
            self.empleados[empleado.id_empleado] = empleado

        # Guardar empleados
        self.guardar_empleados_csv()
    
        # Inicializar inventario con ingredientes
        ingredientes = {
            "cafe": (5000, "Proveedor Café S.A."),
            "leche": (10000, "Lácteos Frescos"),
            "leche_almendra": (5000, "VeganoPro"),
            "azucar": (20000, "Dulzor Natural"),
            "chocolate": (8000, "ChocoMundo"),
            "huevos": (2000, "Granja Feliz"),
            "harina": (15000, "Molinos Unidos"),
            "frutas": (3000, "Frutas Frescas"),
            "crema": (5000, "Lácteos Frescos"),
            "canela": (3000, "Especias Selectas"),
            "vainilla": (2000, "Especias Selectas"),
            "caramelo": (4000, "Dulzor Natural"),
            "miel": (3000, "Dulzor Natural"),
            "matcha": (2000, "Té Premium"),
            "hielo": (10000, "Hielo Puro"),
            "avena": (5000, "Cereales Saludables"),
            "almendras": (4000, "Frutos Secos Selectos"),
            "mantequilla": (6000, "Lácteos Frescos"),
            "queso_crema": (4000, "Lácteos Frescos"),
            "arandanos": (3000, "Frutas Frescas"),
            "chispas_chocolate": (5000, "ChocoMundo"),
            "nueces": (4000, "Frutos Secos Selectos"),
            "mermelada": (3000, "Dulzor Natural"),
            "te_negro": (3000, "Té Premium")
        }
        
        for ing, (cant, prov) in ingredientes.items():
            self.inventario.agregar_ingrediente(ing, cant, prov, umbral=500)
        
        # Crear y agregar bebidas al menú
        bebidas = [
            # Café y bebidas calientes
            Bebida(nombre="Café Americano", precio_base=2.50, 
                   descripcion="Café negro tradicional", tipo=TipoBebida.CALIENTE,
                   precios_tamanos={"pequeño": 2.20, "mediano": 2.50, "grande": 2.80},
                   tiempo_preparacion=3),
            Bebida(nombre="Café con Leche", precio_base=3.00, 
                   descripcion="Café con leche cremosa", tipo=TipoBebida.CALIENTE,
                   precios_tamanos={"pequeño": 2.70, "mediano": 3.00, "grande": 3.30},
                   tiempo_preparacion=4),
            Bebida(nombre="Latte", precio_base=3.50, 
                   descripcion="Café con leche vaporizada", tipo=TipoBebida.CALIENTE,
                   precios_tamanos={"pequeño": 3.20, "mediano": 3.50, "grande": 3.80},
                   tiempo_preparacion=5),
            Bebida(nombre="Capuchino", precio_base=3.75, 
                   descripcion="Café con leche espumosa", tipo=TipoBebida.CALIENTE,
                   precios_tamanos={"pequeño": 3.40, "mediano": 3.75, "grande": 4.10},
                   tiempo_preparacion=5),
            Bebida(nombre="Mocaccino", precio_base=4.00, 
                   descripcion="Café con chocolate y leche", tipo=TipoBebida.CALIENTE,
                   precios_tamanos={"pequeño": 3.60, "mediano": 4.00, "grande": 4.40},
                   tiempo_preparacion=6),
            Bebida(nombre="Té Verde", precio_base=2.50, 
                   descripcion="Té verde tradicional", tipo=TipoBebida.CALIENTE,
                   precios_tamanos={"pequeño": 2.20, "mediano": 2.50, "grande": 2.80},
                   tiempo_preparacion=3),
            Bebida(nombre="Té Negro", precio_base=2.50, 
                   descripcion="Té negro clásico", tipo=TipoBebida.CALIENTE,
                   precios_tamanos={"pequeño": 2.20, "mediano": 2.50, "grande": 2.80},
                   tiempo_preparacion=3),
            Bebida(nombre="Chocolate Caliente", precio_base=3.25, 
                   descripcion="Chocolate cremoso", tipo=TipoBebida.CALIENTE,
                   precios_tamanos={"pequeño": 2.90, "mediano": 3.25, "grande": 3.60},
                   tiempo_preparacion=4),

            # Bebidas frías
            Bebida(nombre="Frappé", precio_base=4.50, 
                   descripcion="Bebida fría con café", tipo=TipoBebida.FRIA,
                   precios_tamanos={"pequeño": 4.00, "mediano": 4.50, "grande": 5.00},
                   tiempo_preparacion=7),
            Bebida(nombre="Té Helado", precio_base=3.00, 
                   descripcion="Té negro frío", tipo=TipoBebida.FRIA,
                   precios_tamanos={"pequeño": 2.70, "mediano": 3.00, "grande": 3.30},
                   tiempo_preparacion=5),
            Bebida(nombre="Limonada Natural", precio_base=3.50, 
                   descripcion="Limonada fresca", tipo=TipoBebida.FRIA,
                   precios_tamanos={"pequeño": 3.20, "mediano": 3.50, "grande": 3.80},
                   tiempo_preparacion=5),
            Bebida(nombre="Granita de Café", precio_base=4.00, 
                   descripcion="Café con hielo frappé", tipo=TipoBebida.FRIA,
                   precios_tamanos={"pequeño": 3.60, "mediano": 4.00, "grande": 4.40},
                   tiempo_preparacion=6),

            # Batidos
            Bebida(nombre="Smoothie de Frutas", precio_base=4.75, 
                   descripcion="Mezcla de frutas naturales", tipo=TipoBebida.BATIDO,
                   precios_tamanos={"pequeño": 4.30, "mediano": 4.75, "grande": 5.20},
                   tiempo_preparacion=8),
            Bebida(nombre="Batido de Chocolate", precio_base=4.50, 
                   descripcion="Batido cremoso de chocolate", tipo=TipoBebida.BATIDO,
                   precios_tamanos={"pequeño": 4.00, "mediano": 4.50, "grande": 5.00},
                   tiempo_preparacion=7),
            Bebida(nombre="Batido de Vainilla", precio_base=4.50, 
                   descripcion="Batido cremoso de vainilla", tipo=TipoBebida.BATIDO,
                   precios_tamanos={"pequeño": 4.00, "mediano": 4.50, "grande": 5.00},
                   tiempo_preparacion=7),
            Bebida(nombre="Batido de Fresa", precio_base=4.75, 
                   descripcion="Batido cremoso de fresa", tipo=TipoBebida.BATIDO,
                   precios_tamanos={"pequeño": 4.30, "mediano": 4.75, "grande": 5.20},
                   tiempo_preparacion=8),
            Bebida(nombre="Batido de Mango", precio_base=4.75, 
                   descripcion="Batido cremoso de mango", tipo=TipoBebida.BATIDO,
                   precios_tamanos={"pequeño": 4.30, "mediano": 4.75, "grande": 5.20},
                   tiempo_preparacion=8),
            Bebida(nombre="Batido Vegano", precio_base=5.00, 
                   descripcion="Batido con leche de almendras", tipo=TipoBebida.BATIDO,
                   precios_tamanos={"pequeño": 4.50, "mediano": 5.00, "grande": 5.50},
                   tiempo_preparacion=8)
        ]
        
            # Configurar ingredientes para las bebidas
        bebidas[0].ingredientes_base = {"cafe": 30}  # Café Americano
        bebidas[1].ingredientes_base = {"cafe": 20, "leche": 100}  # Café con Leche
        bebidas[2].ingredientes_base = {"cafe": 20, "leche": 150}  # Latte
        bebidas[3].ingredientes_base = {"cafe": 20, "leche": 150, "crema": 20}  # Capuchino
        bebidas[4].ingredientes_base = {"cafe": 20, "leche": 100, "chocolate": 30}  # Mocaccino
        bebidas[5].ingredientes_base = {"matcha": 20}  # Té Verde
        bebidas[6].ingredientes_base = {"te_negro": 20}  # Té Negro
        bebidas[7].ingredientes_base = {"chocolate": 40, "leche": 150}  # Chocolate Caliente
        bebidas[8].ingredientes_base = {"cafe": 20, "leche": 100, "hielo": 50}  # Frappé
        bebidas[9].ingredientes_base = {"te_negro": 30, "hielo": 50}  # Té Helado
        bebidas[10].ingredientes_base = {"limon": 50, "azucar": 20, "hielo": 50}  # Limonada Natural
        bebidas[11].ingredientes_base = {"cafe": 30, "hielo": 70, "azucar": 20}  # Granita de Café
        bebidas[12].ingredientes_base = {"frutas": 100, "leche": 150, "hielo": 30}  # Smoothie de Frutas
        bebidas[13].ingredientes_base = {"chocolate": 40, "leche": 150, "hielo": 30}  # Batido de Chocolate
        bebidas[14].ingredientes_base = {"vainilla": 10, "leche": 150, "hielo": 30}  # Batido de Vainilla
        bebidas[15].ingredientes_base = {"frutas": 80, "leche": 150, "hielo": 30}  # Batido de Fresa
        bebidas[16].ingredientes_base = {"frutas": 80, "leche": 150, "hielo": 30}  # Batido de Mango
        bebidas[17].ingredientes_base = {"frutas": 80, "leche_almendra": 150, "hielo": 30}  # Batido Vegano
    
        for bebida in bebidas:
            self.agregar_al_menu(bebida)
        
        # Crear y agregar postres al menú
        postres = [
            Postre("Croissant", 2.50, "Croissant de mantequilla", 
                   tiempo_preparacion=2, es_vegano=False, sin_gluten=False),
            Postre("Croissant de Almendra", 3.50, "Croissant relleno de almendra", 
                   tiempo_preparacion=3, es_vegano=False, sin_gluten=False),
            Postre("Muffin de Arándanos", 3.00, "Muffin casero con arándanos", 
                   tiempo_preparacion=4, es_vegano=False, sin_gluten=False),
            Postre("Muffin de Chocolate", 3.25, "Muffin con chispas de chocolate", 
                   tiempo_preparacion=4, es_vegano=False, sin_gluten=False),
            Postre("Galleta Vegana", 2.50, "Galleta sin productos animales", 
                   tiempo_preparacion=3, es_vegano=True, sin_gluten=False),
            Postre("Brownie Sin Gluten", 3.50, "Brownie de chocolate sin gluten", 
                   tiempo_preparacion=5, es_vegano=False, sin_gluten=True),
            Postre("Brownie Clásico", 3.25, "Brownie de chocolate tradicional", 
                   tiempo_preparacion=5, es_vegano=False, sin_gluten=False),
            Postre("Cheesecake", 4.50, "Porción de cheesecake clásico", 
                   tiempo_preparacion=2, es_vegano=False, sin_gluten=False),
            Postre("Cheesecake de Frutos Rojos", 5.00, "Cheesecake con salsa de frutos rojos", 
                   tiempo_preparacion=2, es_vegano=False, sin_gluten=False),
            Postre("Tarta de Manzana", 4.00, "Porción de tarta de manzana", 
                   tiempo_preparacion=3, es_vegano=False, sin_gluten=False),
            Postre("Tarta de Chocolate", 4.25, "Porción de tarta de chocolate", 
                   tiempo_preparacion=3, es_vegano=False, sin_gluten=False),
            Postre("Donut", 2.75, "Donut glaseado", 
                   tiempo_preparacion=2, es_vegano=False, sin_gluten=False),
            Postre("Donut de Chocolate", 3.00, "Donut cubierto de chocolate", 
                   tiempo_preparacion=2, es_vegano=False, sin_gluten=False),
            Postre("Pan de Canela", 3.50, "Pan dulce con canela", 
                   tiempo_preparacion=3, es_vegano=False, sin_gluten=False),
            Postre("Alfajor", 3.25, "Alfajor relleno de dulce de leche", 
                   tiempo_preparacion=2, es_vegano=False, sin_gluten=False),
            Postre("Trufa de Chocolate", 2.50, "Bola de chocolate rellena", 
                   tiempo_preparacion=2, es_vegano=False, sin_gluten=False),
            Postre("Flan", 3.75, "Porción de flan casero", 
                   tiempo_preparacion=2, es_vegano=False, sin_gluten=False),
            Postre("Crepe de Nutella", 4.50, "Crepe relleno de Nutella", 
                   tiempo_preparacion=6, es_vegano=False, sin_gluten=False),
            Postre("Crepe de Manzana", 4.25, "Crepe con manzana caramelizada", 
                   tiempo_preparacion=6, es_vegano=False, sin_gluten=False),
            Postre("Bagel con Queso Crema", 3.50, "Bagel tostado con queso crema", 
                   tiempo_preparacion=3, es_vegano=False, sin_gluten=False)
        ]
        
        # Configurar ingredientes para los postres
        postres[0].ingredientes_base = {"harina": 80, "huevos": 1, "mantequilla": 30}  # Croissant
        postres[1].ingredientes_base = {"harina": 80, "huevos": 1, "mantequilla": 30, "almendras": 40}  # Croissant Almendra
        postres[2].ingredientes_base = {"harina": 100, "huevos": 1, "arandanos": 30, "mantequilla": 20}  # Muffin Arándanos
        postres[3].ingredientes_base = {"harina": 100, "huevos": 1, "chispas_chocolate": 40, "mantequilla": 20}  # Muffin Chocolate
        postres[4].ingredientes_base = {"harina": 60, "avena": 30, "leche_almendra": 20}  # Galleta Vegana
        postres[5].ingredientes_base = {"harina": 50, "chocolate": 40, "huevos": 1}  # Brownie Sin Gluten
        postres[6].ingredientes_base = {"harina": 60, "chocolate": 50, "huevos": 1, "mantequilla": 30}  # Brownie Clásico
        postres[7].ingredientes_base = {"queso_crema": 80, "huevos": 1, "azucar": 30}  # Cheesecake
        postres[8].ingredientes_base = {"queso_crema": 80, "huevos": 1, "azucar": 30, "arandanos": 30}  # Cheesecake Frutos Rojos
        postres[9].ingredientes_base = {"harina": 70, "frutas": 50, "mantequilla": 20}  # Tarta Manzana
        postres[10].ingredientes_base = {"harina": 70, "chocolate": 60, "mantequilla": 20}  # Tarta Chocolate
        postres[11].ingredientes_base = {"harina": 60, "azucar": 30, "huevos": 1}  # Donut
        postres[12].ingredientes_base = {"harina": 60, "azucar": 30, "huevos": 1, "chocolate": 30}  # Donut Chocolate
        postres[13].ingredientes_base = {"harina": 80, "canela": 10, "mantequilla": 20}  # Pan Canela
        postres[14].ingredientes_base = {"harina": 50, "mermelada": 30}  # Alfajor
        postres[15].ingredientes_base = {"chocolate": 40, "crema": 20}  # Trufa
        postres[16].ingredientes_base = {"huevos": 1, "leche": 50, "azucar": 30}  # Flan
        postres[17].ingredientes_base = {"harina": 50, "huevos": 1, "chocolate": 40}  # Crepe Nutella
        postres[18].ingredientes_base = {"harina": 50, "huevos": 1, "frutas": 40, "caramelo": 20}  # Crepe Manzana
        postres[19].ingredientes_base = {"harina": 80, "queso_crema": 50}  # Bagel
        
        for postre in postres:
            self.agregar_al_menu(postre)
        
        # Crear promociones
        current_year = datetime.now().year
        self.promociones = [
            Promocion(
                "Descuento por Puntos", 
                10, 
                "PUNTOS10", 
                datetime.now(), 
                datetime(current_year + 1, 12, 31),
                puntos_requeridos=50
            ),
            Promocion(
                "Combo Desayuno", 
                15, 
                "DESAYUNO15", 
                datetime.now(), 
                datetime(current_year, 12, 31),
                productos_minimos=3
            ),
            Promocion(
                "Martes de Postre", 
                20, 
                "POSTRE20", 
                datetime.now(), 
                datetime(current_year, 12, 31)
            ),
            Promocion(
                "Bebida Gratis", 
                100, 
                "BEBIDAG", 
                datetime.now(), 
                datetime(current_year, 12, 31),
                productos_minimos=4
            )
        ]

    def agregar_al_menu(self, producto: ProductoBase) -> None:
        if producto.nombre in self.menu:
            raise ValueError(f"El producto {producto.nombre} ya está en el menú")
        self.menu[producto.nombre] = producto

