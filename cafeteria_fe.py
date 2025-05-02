import tkinter as tk
import traceback
from tkinter import ttk, messagebox
from cafeteria_be import Cafeteria, Bebida, Postre, Cliente, Empleado, RolEmpleado, TipoBebida, ProductoPersonalizado, Promocion, Pedido, ProductoBase, Persona
from datetime import datetime, timedelta
import os

class CafeteriaApp:
    def __init__(self, root):
        DEBUG_MODE = True  # Cambia a False para producción
        self.root = root
        self.root.title("Sistema de Cafetería")
        self.root.geometry("1200x800")

        # Inicializar la cafetería
        self.cafe = Cafeteria(
            nombre="Cafetería Delicioso",
            direccion="Av. Principal 123",
            telefono="555-1234"
        )

        # Cargar datos de prueba
        try:
            self.cafe.inicializar_datos_prueba()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar datos: {str(e)}")

        self.usuario_actual = None
        self.productos_pedido = []
        self.current_admin_frame = None

        self.cafe.cargar_clientes_csv()  # Cargar clientes desde CSV al inicio
        self.cafe.cargar_empleados_csv()
      

        # Verificación simplificada de usuarios
        print("\nVerificación de usuarios:")
        for cliente in self.cafe.clientes.values():
            print(f"Cliente {cliente.id}: Contraseña {'correcta' if cliente.contrasena == '123456' else 'incorrecta'}")
        for empleado in self.cafe.empleados.values():
            print(f"Empleado {empleado.id_empleado}: Contraseña {'correcta' if empleado.contrasena == '123456' else 'incorrecta'}")

        self._configurar_estilos()
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.cafe.cargar_clientes_csv()  # Cargar clientes desde CSV al inicio
        self.mostrar_login()
    
        # Verificación simplificada de usuarios (opcional, solo para desarrollo)
        if DEBUG_MODE:  # Añade DEBUG_MODE = True al inicio del archivo si quieres mantener esto
            print("\nVerificación de usuarios (solo desarrollo):")
            for cliente in self.cafe.clientes.values():
                if hasattr(cliente, 'verificar_contrasena'):
                    print(f"Cliente {cliente.id}: {'OK' if cliente.verificar_contrasena('123456') else 'Error'}")

            for empleado in self.cafe.empleados.values():
                if hasattr(empleado, 'verificar_contrasena'):
                    print(f"Empleado {empleado.id_empleado}: {'OK' if empleado.verificar_contrasena('123456') else 'Error'}")

    def _cargar_menu_basico(self):
        """Carga un menú mínimo para que la aplicación funcione"""
        try:
            # Verificar si el producto ya existe antes de agregarlo
            if "Café Americano" not in self.cafe.menu:
                cafe_americano = Bebida("Café Americano", 2.50, "Café negro tradicional", 
                                       TipoBebida.CALIENTE, tiempo_preparacion=3)
                cafe_americano.ingredientes_base = {"cafe": 30}
                self.cafe.agregar_al_menu(cafe_americano)

            if "Croissant" not in self.cafe.menu:
                croissant = Postre("Croissant", 2.50, "Croissant de mantequilla", 
                                  tiempo_preparacion=2, es_vegano=False, sin_gluten=False)
                croissant.ingredientes_base = {"harina": 80, "mantequilla": 30}
                self.cafe.agregar_al_menu(croissant)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el menú básico: {str(e)}")
    
    def focus_first_entry(self):
        """Enfoca el primer campo de entrada disponible"""
        if hasattr(self, 'login_entries') and self.login_entries:
            self.login_entries['usuario'].focus_set()
        elif hasattr(self, 'registro_entries') and self.registro_entries:
            self.registro_entries['nombre'].focus_set()
    def limpiar_pantalla(self):
        """Limpia todos los widgets del contenedor principal"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def _configurar_estilos(self):
        """Configura los estilos visuales de la aplicación"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configuraciones de estilo
        self.style.configure('TFrame', background='#f5f5f5')
        self.style.configure('TLabel', background='#f5f5f5', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        
        # Estilos personalizados
        self.style.configure('Header.TLabel', font=('Arial', 14, 'bold'))
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2c3e50')
        self.style.configure('Primary.TButton', foreground='white', background='#3498db')
        self.style.configure('Secondary.TButton', foreground='white', background='#7f8c8d')
        self.style.configure('Success.TButton', foreground='white', background='#2ecc71')
        self.style.configure('Danger.TButton', foreground='white', background='#e74c3c')
        self.style.configure('Info.TButton', foreground='white', background='#1abc9c')
        self.style.configure('Warning.TButton', foreground='white', background='#f39c12')
    
    def mostrar_login(self):
        """Muestra la pantalla de inicio de sesión mejorada"""
        self.limpiar_pantalla()

        login_frame = tk.Frame(self.main_frame, bg="#f5f5f5", padx=20, pady=20)
        login_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            login_frame,
            text="Inicio de Sesión",
            font=("Arial", 16, "bold"),
            bg="#f5f5f5"
        ).pack(pady=10)

        # Campos del formulario
        campos = [
            ("Usuario (ID o Email):", "usuario"),
            ("Contraseña:", "contrasena", "*")
        ]

        self.login_entries = {}
        for campo in campos:
            label_text, field_name, *show = campo
            tk.Label(
                login_frame,
                text=label_text,
                font=("Arial", 12),
                bg="#f5f5f5"
            ).pack(anchor=tk.W, pady=5)

            entry = tk.Entry(
                login_frame,
                show=show[0] if show else "",
                font=("Arial", 12),
                relief=tk.SOLID,
                bd=1
            )
            entry.pack(fill=tk.X, pady=5)
            self.login_entries[field_name] = entry

        # Botones
        button_frame = tk.Frame(login_frame, bg="#f5f5f5")
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Iniciar Sesión",
            command=self.procesar_login,
            font=("Arial", 12),
            bg="#2ecc71",
            fg="white",
            relief=tk.FLAT,
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Registrarse",
            command=self.mostrar_registro,
            font=("Arial", 12),
            bg="#3498db",
            fg="white",
            relief=tk.FLAT,
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)

        # Enfocar el primer campo
        self.login_entries["usuario"].focus_set()
        self.root.bind('<Return>', lambda event: self.procesar_login())


    def mostrar_registro(self):
        """Muestra la pantalla de registro mejorada"""
        self.limpiar_pantalla()

        registro_frame = ttk.Frame(self.main_frame, padding=20)
        registro_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(registro_frame, text="Registro de Nuevo Cliente", style='Header.TLabel').pack(pady=10)

        # Campos del formulario
        campos = [
            ("Nombre Completo:", "nombre"),
            ("ID (Cédula):", "id"),
            ("Teléfono:", "telefono"),
            ("Email:", "email"),
            ("Contraseña (mínimo 6 caracteres):", "contrasena", "*"),
            ("Confirmar Contraseña:", "confirmar_contrasena", "*")
        ]

        self.registro_entries = {}
        for campo in campos:
            label_text, field_name, *show = campo
            ttk.Label(registro_frame, text=label_text).pack(anchor=tk.W, pady=5)

            entry = tk.Entry(
                registro_frame, 
                show=show[0] if show else "",
                font=('Arial', 10),
                relief=tk.SOLID,
                highlightthickness=1
            )
            entry.pack(fill=tk.X, pady=5)
            self.registro_entries[field_name] = entry

        # Enfocar el primer campo
        self.registro_entries['nombre'].focus_set()
        self.root.bind('<Return>', lambda event: self.procesar_registro())

        # Botones
        button_frame = ttk.Frame(registro_frame)
        button_frame.pack(pady=10)

        ttk.Button(
            button_frame,
            text="Registrarse",
            command=self.procesar_registro,
            style='Success.TButton'
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Volver",
            command=self.mostrar_login,
            style='Secondary.TButton'
        ).pack(side=tk.LEFT, padx=5)

    def procesar_registro(self):
        """Procesa el registro con validación mejorada y manejo de errores"""
        datos = {k: v.get().strip() for k, v in self.registro_entries.items()}
    
        # Validaciones mejoradas
        if not all(datos.values()):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
    
        if len(datos["contrasena"]) < 6:
            messagebox.showerror("Error", "La contraseña debe tener al menos 6 caracteres")
            return
    
        if datos["contrasena"] != datos["confirmar_contrasena"]:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
    
        if not '@' in datos["email"] or '.' not in datos["email"].split('@')[-1]:
            messagebox.showerror("Error", "Ingrese un email válido")
            return
    
        try:
            # Crear cliente con datos normalizados
            nuevo_cliente = Cliente(
                nombre=datos["nombre"],
                id=datos["id"],
                telefono=datos["telefono"],
                email=datos["email"].lower().strip(),
                contrasena=datos["contrasena"].strip()
            )
    
            # Registrar y actualizar lista en memoria
            self.cafe.registrar_cliente(nuevo_cliente)
            
            # Guardar cambios en CSV inmediatamente
            self.cafe.guardar_clientes_csv()
            
            # Recargar clientes desde CSV para asegurar consistencia
            self.cafe.clientes = {}  # Limpiar diccionario actual
            self.cafe.cargar_clientes_csv()
            
            # Buscar el cliente recién registrado en los datos cargados
            usuario_registrado = None
            for cliente in self.cafe.clientes.values():
                if cliente.email.lower() == nuevo_cliente.email.lower() or cliente.id == nuevo_cliente.id:
                    usuario_registrado = cliente
                    break
                
            if usuario_registrado:
                self.usuario_actual = usuario_registrado
                messagebox.showinfo("Éxito", f"¡Registro completado! Bienvenido {nuevo_cliente.nombre}")
                self.mostrar_menu_principal()
            else:
                messagebox.showerror("Error", "Registro completado pero no se pudo autenticar. Por favor inicie sesión manualmente.")
                self.mostrar_login()
    
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error en el registro: {str(e)}")
            print(f"Error detallado: {traceback.format_exc()}")

    def procesar_login(self):
        """Procesa el formulario de inicio de sesión con mejor manejo de errores"""
        usuario = self.login_entries['usuario'].get().strip()
        contrasena = self.login_entries['contrasena'].get()

        if not usuario or not contrasena:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        try:
            persona = self.cafe.autenticar_usuario(usuario, contrasena)

            if persona:
                self.usuario_actual = persona
                messagebox.showinfo("Éxito", f"¡Bienvenido {self.usuario_actual.nombre}!")
                self.mostrar_menu_principal()
            else:
                messagebox.showerror("Error", "Credenciales incorrectas")
                self.login_entries['contrasena'].delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Error en el sistema: {str(e)}")
            print(f"Error detallado en autenticación: {e}")

        
    def cerrar_sesion(self):
        """Cierra la sesión actual y vuelve al login"""
        self.usuario_actual = None
        self.productos_pedido = []
        self.mostrar_login()
    
    def mostrar_menu_principal(self):
        """Muestra el menú principal después del login"""
        self.limpiar_pantalla()
    
        # Barra de usuario
        user_frame = ttk.Frame(self.main_frame)
        user_frame.pack(fill=tk.X, padx=10, pady=5)
    
        ttk.Label(
            user_frame,
            text=f"Bienvenido: {self.usuario_actual.nombre}",
            style='Header.TLabel'
        ).pack(side=tk.LEFT)
    
        if hasattr(self.usuario_actual, 'puntos_fidelidad'):
            self.puntos_label = ttk.Label(
                user_frame,
                text=f"Puntos: {self.usuario_actual.puntos_fidelidad}",
                style='Header.TLabel',
                foreground='#3498db'
            )
            self.puntos_label.pack(side=tk.LEFT, padx=10)
    
        ttk.Button(
            user_frame,
            text="Cerrar Sesión",
            command=self.cerrar_sesion,
            style='Danger.TButton'
        ).pack(side=tk.RIGHT)
    
        # Opciones principales
        options_frame = ttk.Frame(self.main_frame)
        options_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
        ttk.Label(options_frame, text="Menú Principal", style='Title.TLabel').pack(pady=20)
    
        # Botones según tipo de usuario
        button_frame = ttk.Frame(options_frame)
        button_frame.pack(pady=10)
    
        # Opciones comunes para todos los usuarios
        ttk.Button(
            button_frame,
            text="Ver Menú",
            command=self.mostrar_menu_completo,
            style='Primary.TButton',
            width=20
        ).pack(pady=10, fill=tk.X)
    
        ttk.Button(
            button_frame,
            text="Realizar Pedido",
            command=self.mostrar_realizar_pedido,
            style='Success.TButton',
            width=20
        ).pack(pady=10, fill=tk.X)
    
        # Opciones específicas para clientes
        if not hasattr(self.usuario_actual, 'rol'):
            ttk.Button(
                button_frame,
                text="Historial de Pedidos",
                command=self._mostrar_historial_pedidos,
                style='Secondary.TButton',
                width=20
            ).pack(pady=10, fill=tk.X)
    
        # Opciones específicas para empleados
        if hasattr(self.usuario_actual, 'rol'):
            if self.usuario_actual.rol == RolEmpleado.GERENTE:
                ttk.Button(
                    button_frame,
                    text="Administración",
                    command=self.mostrar_administracion,
                    style='Warning.TButton',
                    width=20
                ).pack(pady=10, fill=tk.X)

    def mostrar_administracion(self):
        """Muestra el panel de administración para gerentes"""
        self.limpiar_pantalla()

        # Frame principal
        main_frame = ttk.Frame(self.main_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(
            main_frame,
            text="Panel de Administración",
            style='Title.TLabel'
        ).pack(pady=10)

        # Crear notebook (pestañas)
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Pestaña de Productos
        productos_frame = ttk.Frame(notebook)
        notebook.add(productos_frame, text="Productos")
        self._mostrar_admin_productos(productos_frame)

        # Botón para volver
        ttk.Button(
            main_frame,
            text="Volver al Menú Principal",
            command=self.mostrar_menu_principal,
            style='Secondary.TButton'
        ).pack(pady=10)
        
    def _mostrar_admin_productos(self, frame):
        """Muestra la administración de productos"""
        self.current_admin_frame = frame
        for widget in frame.winfo_children():
            widget.destroy()

        # Botón para agregar nuevo producto
        ttk.Button(
            frame,
            text="+ Agregar Nuevo Producto",
            command=self._agregar_nuevo_producto,
            style='Success.TButton'
        ).pack(pady=10, anchor=tk.NE)

        # Treeview para productos
        columns = ("#1", "#2", "#3", "#4", "#5")
        tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=15
        )

        # Configurar columnas
        tree.heading("#1", text="Nombre")
        tree.heading("#2", text="Tipo")
        tree.heading("#3", text="Precio")
        tree.heading("#4", text="Tiempo Prep.")
        tree.heading("#5", text="Detalles")

        tree.column("#1", width=150, anchor=tk.W)
        tree.column("#2", width=100, anchor=tk.W)
        tree.column("#3", width=80, anchor=tk.E)
        tree.column("#4", width=80, anchor=tk.CENTER)
        tree.column("#5", width=150, anchor=tk.W)

        # Llenar con datos
        for nombre, producto in self.cafe.menu.items():
            if isinstance(producto, Bebida):
                detalles = f"Tipo: {producto.tipo.value}"
            else:
                detalles = "Vegano" if producto.es_vegano else "No vegano"
                if producto.sin_gluten:
                    detalles += ", Sin gluten"

            tree.insert("", tk.END, values=(
                nombre,
                "Bebida" if isinstance(producto, Bebida) else "Postre",
                f"${producto.precio_base:.2f}",
                f"{producto.tiempo_preparacion} min",
                detalles
            ))

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Botones de acción
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=5)

        ttk.Button(
            button_frame,
            text="Editar Seleccionado",
            command=lambda: self._editar_producto(tree),
            style='Info.TButton'
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Eliminar Seleccionado",
            command=lambda: self._eliminar_producto(tree),
            style='Danger.TButton'
        ).pack(side=tk.LEFT, padx=5)

    def _agregar_producto(self, producto_base: ProductoBase):
        """Versión completamente funcional para agregar productos al pedido"""
        print("[DEBUG] Función agregar_producto_pedido llamada")  # Debe aparecer al clickear el botón
        # Verificar que tenemos donde almacenar el pedido
        if not hasattr(self, 'productos_pedido'):
            self.productos_pedido = []

        # Crear ventana de personalización
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Personalizar {producto_base.nombre}")
        dialog.geometry("400x400")
        dialog.transient(self.root)
        dialog.grab_set()

        # Variables para las opciones
        tamano_var = tk.StringVar(value="mediano")
        notas_var = tk.StringVar()
        modificaciones = {}

        # Frame principal con scrollbar
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Tamaño (solo para bebidas)
        if isinstance(producto_base, Bebida):
            ttk.Label(scrollable_frame, text="Tamaño:").pack(anchor=tk.W, pady=5)
            for tamano in producto_base.tamanos_disponibles:
                ttk.Radiobutton(
                    scrollable_frame,
                    text=tamano.capitalize(),
                    variable=tamano_var,
                    value=tamano
                ).pack(anchor=tk.W)

        # Modificaciones de ingredientes
        if hasattr(producto_base, 'ingredientes_base'):
            ttk.Label(scrollable_frame, text="Modificaciones:").pack(anchor=tk.W, pady=5)

            for ingrediente in producto_base.ingredientes_base.keys():
                frame = ttk.Frame(scrollable_frame)
                frame.pack(fill=tk.X, pady=2)

                ttk.Label(frame, text=f"{ingrediente.capitalize()}:").pack(side=tk.LEFT)

                combo_var = tk.StringVar(value="Normal")
                ttk.OptionMenu(
                    frame, 
                    combo_var, 
                    "Normal", 
                    "Normal", 
                    "Extra", 
                    "Sin"
                ).pack(side=tk.LEFT, padx=5)

                # Guardar referencia para capturar la selección después
                modificaciones[ingrediente] = combo_var

        # Notas especiales
        ttk.Label(scrollable_frame, text="Notas especiales:").pack(anchor=tk.W, pady=5)
        ttk.Entry(scrollable_frame, textvariable=notas_var).pack(fill=tk.X, pady=5)

        

        # Función para procesar el producto
        def procesar_producto():
            print("[DEBUG] Botón procesar_producto clickeado")
            try:
                print("[DEBUG] Intentando crear producto...")
                # Procesar modificaciones
                mods_final = {}
                for ingrediente, var in modificaciones.items():
                    opcion = var.get()
                    if opcion == "Extra":
                        mods_final[ingrediente] = 1  # +1 porción extra
                    elif opcion == "Sin":
                        mods_final[ingrediente] = -1  # Eliminar ingrediente

                # Crear producto personalizado
                producto = ProductoPersonalizado(
                    producto_base=producto_base,
                    tamano=tamano_var.get(),
                    notas=notas_var.get(),
                    modificaciones=mods_final
                )

                # Agregar al pedido
                self.productos_pedido.append(producto)

                # Actualizar interfaz si los elementos existen
                if hasattr(self, 'pedido_listbox'):
                    self.pedido_listbox.insert(tk.END, producto.nombre)

                if hasattr(self, 'total_pedido'):
                    nuevo_total = round(self.total_pedido.get() + producto.precio_final, 2)
                    self.total_pedido.set(nuevo_total)
                    self.total_str.set(f"Total: ${nuevo_total:.2f}")

                messagebox.showinfo("Éxito", f"Producto agregado:\n{producto.nombre}")
                dialog.destroy()

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo agregar el producto:\n{str(e)}")

        # Botones
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(pady=10)

        ttk.Button(
            button_frame,
            text="Agregar al Pedido",
            command=procesar_producto,
            style='Success.TButton'
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Cancelar",
            command=dialog.destroy,
            style='Danger.TButton'
        ).pack(side=tk.LEFT, padx=5)

        # Enfocar la ventana
        dialog.focus_set()

    def _agregar_nuevo_producto(self):
        """Muestra el formulario para agregar nuevo producto"""
        if not hasattr(self, 'current_admin_frame') or self.current_admin_frame is None:
            messagebox.showerror("Error", "No se puede determinar dónde mostrar el formulario")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Nuevo Producto")
        dialog.geometry("500x550")
        dialog.transient(self.root)
        dialog.grab_set()

        # Variables del formulario
        tipo_var = tk.StringVar(value="bebida")
        nombre_var = tk.StringVar()
        precio_var = tk.DoubleVar(value=2.0)
        descripcion_var = tk.StringVar()
        tiempo_var = tk.IntVar(value=5)

        # Campos del formulario
        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Tipo de producto
        ttk.Label(main_frame, text="Tipo de Producto:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(main_frame, text="Bebida", variable=tipo_var, value="bebida").grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(main_frame, text="Postre", variable=tipo_var, value="postre").grid(row=0, column=2, sticky=tk.W)

        # Nombre
        ttk.Label(main_frame, text="Nombre del Producto:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=nombre_var).grid(row=1, column=1, columnspan=2, sticky=tk.EW, pady=5)

        # Precio
        ttk.Label(main_frame, text="Precio Base:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=precio_var).grid(row=2, column=1, sticky=tk.W, pady=5)

        # Tiempo de preparación
        ttk.Label(main_frame, text="Tiempo Preparación (min):").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=tiempo_var).grid(row=3, column=1, sticky=tk.W, pady=5)

        # Descripción
        ttk.Label(main_frame, text="Descripción:").grid(row=4, column=0, sticky=tk.W, pady=5)
        desc_entry = ttk.Entry(main_frame, textvariable=descripcion_var)
        desc_entry.grid(row=4, column=1, columnspan=2, sticky=tk.EW, pady=5)

        # Campos específicos para bebidas
        tipo_bebida_var = tk.StringVar(value=TipoBebida.CALIENTE.value)
        ttk.Label(main_frame, text="Tipo de Bebida:").grid(row=5, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(main_frame, text="Caliente", variable=tipo_bebida_var, 
                       value=TipoBebida.CALIENTE.value).grid(row=5, column=1, sticky=tk.W)
        ttk.Radiobutton(main_frame, text="Fría", variable=tipo_bebida_var, 
                       value=TipoBebida.FRIA.value).grid(row=5, column=2, sticky=tk.W)
        ttk.Radiobutton(main_frame, text="Batido", variable=tipo_bebida_var, 
                       value=TipoBebida.BATIDO.value).grid(row=6, column=1, sticky=tk.W)

        # Campos específicos para postres
        es_vegano_var = tk.BooleanVar(value=False)
        sin_gluten_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(main_frame, text="Es Vegano", variable=es_vegano_var).grid(row=7, column=1, sticky=tk.W, pady=5)
        ttk.Checkbutton(main_frame, text="Sin Gluten", variable=sin_gluten_var).grid(row=7, column=2, sticky=tk.W, pady=5)

        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=3, pady=10)

        ttk.Button(
            button_frame,
            text="Guardar Producto",
            command=lambda: self._guardar_producto_completo(
                tipo_var.get(),
                nombre_var.get(),
                precio_var.get(),
                descripcion_var.get(),
                tiempo_var.get(),
                tipo_bebida_var.get() if tipo_var.get() == "bebida" else None,
                es_vegano_var.get() if tipo_var.get() == "postre" else False,
                sin_gluten_var.get() if tipo_var.get() == "postre" else False,
                dialog
            ),
            style='Success.TButton'
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Cancelar",
            command=dialog.destroy,
            style='Danger.TButton'
        ).pack(side=tk.LEFT, padx=5)

        # Configurar grid
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
    def _guardar_producto_completo(self, tipo, nombre, precio, descripcion, tiempo_prep, 
                              tipo_bebida=None, es_vegano=False, sin_gluten=False, dialog=None):
        """Guarda un nuevo producto con todos los atributos"""
        try:
            # Validaciones básicas
            if not nombre.strip():
                raise ValueError("El nombre del producto no puede estar vacío")
            if precio <= 0:
                raise ValueError("El precio debe ser mayor que 0")
            if tiempo_prep < 0:
                raise ValueError("El tiempo de preparación no puede ser negativo")
    
            # Crear el producto según el tipo
            if tipo == "bebida":
                if tipo_bebida not in [t.value for t in TipoBebida]:
                    raise ValueError("Tipo de bebida no válido")
                
                producto = Bebida(
                    nombre=nombre.strip(),
                    precio_base=precio,
                    descripcion=descripcion.strip(),
                    tipo=TipoBebida(tipo_bebida),
                    tiempo_preparacion=tiempo_prep
                )
            else:
                producto = Postre(
                    nombre=nombre.strip(),
                    precio_base=precio,
                    descripcion=descripcion.strip(),
                    tiempo_preparacion=tiempo_prep,
                    es_vegano=es_vegano,
                    sin_gluten=sin_gluten
                )
    
            # Agregar al menú
            self.cafe.agregar_al_menu(producto)
            
            # Mostrar mensaje y cerrar diálogo
            messagebox.showinfo("Éxito", f"Producto '{nombre}' agregado correctamente")
            if dialog:
                dialog.destroy()
            
            # Actualizar la vista de administración
            if hasattr(self, 'current_admin_frame') and self.current_admin_frame:
                self._mostrar_admin_productos(self.current_admin_frame)
    
        except ValueError as e:
            messagebox.showerror("Error de validación", str(e))
        except Exception as e:
            messagebox.showerror("Error inesperado", f"No se pudo guardar el producto: {str(e)}")
            print(f"Error completo: {traceback.format_exc()}")

    def _actualizar_formulario_producto(self, parent_frame, tipo_var):
        """Actualiza los campos específicos según el tipo de producto"""
        for widget in self.campos_especificos_frame.winfo_children():
            widget.destroy()

        if tipo_var.get() == "bebida":
            # Campos específicos para bebidas
            ttk.Label(self.campos_especificos_frame, text="Tipo de Bebida:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=5)

            tipo_bebida_var = tk.StringVar(value=TipoBebida.CALIENTE.value)
            for tipo in TipoBebida:
                ttk.Radiobutton(
                    self.campos_especificos_frame,
                    text=tipo.value.capitalize(),
                    variable=tipo_bebida_var,
                    value=tipo.value
                ).pack(anchor=tk.W)

            # Ingredientes (puedes implementar esto más adelante)
            ttk.Label(self.campos_especificos_frame, text="Ingredientes:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=5)
            ttk.Label(self.campos_especificos_frame, text="(Funcionalidad de ingredientes en desarrollo)").pack(anchor=tk.W)

        else:
            # Campos específicos para postres
            es_vegano_var = tk.BooleanVar(value=False)
            sin_gluten_var = tk.BooleanVar(value=False)

            ttk.Checkbutton(
                self.campos_especificos_frame,
                text="Es Vegano",
                variable=es_vegano_var
            ).pack(anchor=tk.W, pady=5)

            ttk.Checkbutton(
                self.campos_especificos_frame,
                text="Sin Gluten",
                variable=sin_gluten_var
            ).pack(anchor=tk.W, pady=5)

            # Requiere horneado
            requiere_horneado_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(
                self.campos_especificos_frame,
                text="Requiere Horneado",
                variable=requiere_horneado_var
            ).pack(anchor=tk.W, pady=5)

    def _guardar_producto(self, tipo, nombre, precio, descripcion, dialog):
        """Guarda el nuevo producto en el sistema"""
        try:
            if not nombre.strip():
                raise ValueError("El nombre no puede estar vacío")

            if precio <= 0:
                raise ValueError("El precio debe ser mayor que 0")

            if tipo == "bebida":
                producto = Bebida(
                    nombre=nombre.strip(),
                    precio_base=precio,
                    descripcion=descripcion.strip(),
                    tipo=TipoBebida.CALIENTE,
                    tiempo_preparacion=5  # Valor por defecto
                )
            else:
                producto = Postre(
                    nombre=nombre.strip(),
                    precio_base=precio,
                    descripcion=descripcion.strip(),
                    tiempo_preparacion=5  # Valor por defecto
                )

            self.cafe.agregar_al_menu(producto)
            messagebox.showinfo("Éxito", f"Producto '{nombre}' agregado correctamente")
            dialog.destroy()

            # Actualizar la vista solo si tenemos el frame de administración
            if self.current_admin_frame is not None:
                self._mostrar_admin_productos(self.current_admin_frame)

        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")
            print(f"Error completo: {traceback.format_exc()}")  # Para debug

    def _editar_producto(self, tree):
        """Edita el producto seleccionado en el Treeview"""
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto para editar")
            return
        
        item = tree.item(seleccion[0])
        nombre_producto = item['values'][0]
        
        if nombre_producto not in self.cafe.menu:
            messagebox.showerror("Error", "Producto no encontrado en el menú")
            return
        
        producto = self.cafe.menu[nombre_producto]
        self._mostrar_formulario_edicion(producto, tree)
    
    def _mostrar_formulario_edicion(self, producto, tree):
        """Muestra el formulario de edición para un producto existente"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Editar Producto: {producto.nombre}")
        dialog.geometry("500x550")
        dialog.transient(self.root)
        dialog.grab_set()
    
        # Variables del formulario
        nombre_var = tk.StringVar(value=producto.nombre)
        precio_var = tk.DoubleVar(value=producto.precio_base)
        descripcion_var = tk.StringVar(value=producto.descripcion)
        tiempo_var = tk.IntVar(value=producto.tiempo_preparacion)
        
        # Determinar tipo de producto
        es_bebida = isinstance(producto, Bebida)
        tipo_var = tk.StringVar(value="bebida" if es_bebida else "postre")
        
        # Campos del formulario
        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
    
        # Tipo de producto (no editable)
        ttk.Label(main_frame, text="Tipo de Producto:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text="Bebida" if es_bebida else "Postre").grid(row=0, column=1, sticky=tk.W)
    
        # Nombre
        ttk.Label(main_frame, text="Nombre del Producto:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=nombre_var).grid(row=1, column=1, columnspan=2, sticky=tk.EW, pady=5)
    
        # Precio
        ttk.Label(main_frame, text="Precio Base:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=precio_var).grid(row=2, column=1, sticky=tk.W, pady=5)
    
        # Tiempo de preparación
        ttk.Label(main_frame, text="Tiempo Preparación (min):").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=tiempo_var).grid(row=3, column=1, sticky=tk.W, pady=5)
    
        # Descripción
        ttk.Label(main_frame, text="Descripción:").grid(row=4, column=0, sticky=tk.W, pady=5)
        desc_entry = ttk.Entry(main_frame, textvariable=descripcion_var)
        desc_entry.grid(row=4, column=1, columnspan=2, sticky=tk.EW, pady=5)
    
        # Campos específicos para bebidas
        if es_bebida:
            tipo_bebida_var = tk.StringVar(value=producto.tipo.value)
            ttk.Label(main_frame, text="Tipo de Bebida:").grid(row=5, column=0, sticky=tk.W, pady=5)
            ttk.Radiobutton(main_frame, text="Caliente", variable=tipo_bebida_var, 
                           value=TipoBebida.CALIENTE.value).grid(row=5, column=1, sticky=tk.W)
            ttk.Radiobutton(main_frame, text="Fría", variable=tipo_bebida_var, 
                           value=TipoBebida.FRIA.value).grid(row=5, column=2, sticky=tk.W)
            ttk.Radiobutton(main_frame, text="Batido", variable=tipo_bebida_var, 
                           value=TipoBebida.BATIDO.value).grid(row=6, column=1, sticky=tk.W)
        else:
            # Campos específicos para postres
            es_vegano_var = tk.BooleanVar(value=producto.es_vegano)
            sin_gluten_var = tk.BooleanVar(value=producto.sin_gluten)
            ttk.Checkbutton(main_frame, text="Es Vegano", variable=es_vegano_var).grid(row=5, column=1, sticky=tk.W, pady=5)
            ttk.Checkbutton(main_frame, text="Sin Gluten", variable=sin_gluten_var).grid(row=5, column=2, sticky=tk.W, pady=5)
    
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=3, pady=10)
    
        ttk.Button(
            button_frame,
            text="Guardar Cambios",
            command=lambda: self._guardar_cambios_producto(
                producto,
                nombre_var.get(),
                precio_var.get(),
                descripcion_var.get(),
                tiempo_var.get(),
                tipo_bebida_var.get() if es_bebida else None,
                es_vegano_var.get() if not es_bebida else False,
                sin_gluten_var.get() if not es_bebida else False,
                dialog,
                tree
            ),
            style='Success.TButton'
        ).pack(side=tk.LEFT, padx=5)
    
        ttk.Button(
            button_frame,
            text="Cancelar",
            command=dialog.destroy,
            style='Danger.TButton'
        ).pack(side=tk.LEFT, padx=5)
    
        # Configurar grid
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)

    def _guardar_cambios_producto(self, producto_original, nuevo_nombre, nuevo_precio, nueva_descripcion, 
                                nuevo_tiempo, nuevo_tipo_bebida=None, nuevo_es_vegano=False, 
                                nuevo_sin_gluten=False, dialog=None, tree=None):
        """Guarda los cambios realizados a un producto existente"""
        try:
            # Validaciones básicas
            if not nuevo_nombre.strip():
                raise ValueError("El nombre del producto no puede estar vacío")
            if nuevo_precio <= 0:
                raise ValueError("El precio debe ser mayor que 0")
            if nuevo_tiempo < 0:
                raise ValueError("El tiempo de preparación no puede ser negativo")

            nombre_limpio = nuevo_nombre.strip()

            # Solo verificar duplicados si el nombre cambió
            if producto_original.nombre != nombre_limpio and nombre_limpio in self.cafe.menu:
                raise ValueError("Ya existe un producto con ese nombre")

            # Crear una copia del producto original con los nuevos valores
            if isinstance(producto_original, Bebida):
                producto_actualizado = Bebida(
                    nombre=nombre_limpio,
                    precio_base=nuevo_precio,
                    descripcion=nueva_descripcion.strip(),
                    tipo=TipoBebida(nuevo_tipo_bebida),
                    tiempo_preparacion=nuevo_tiempo,
                    ingredientes_base=producto_original.ingredientes_base.copy(),
                    tamanos_disponibles=producto_original.tamanos_disponibles.copy(),
                    precios_tamanos=producto_original.precios_tamanos.copy()
                )
            else:
                producto_actualizado = Postre(
                    nombre=nombre_limpio,
                    precio_base=nuevo_precio,
                    descripcion=nueva_descripcion.strip(),
                    tiempo_preparacion=nuevo_tiempo,
                    es_vegano=nuevo_es_vegano,
                    sin_gluten=nuevo_sin_gluten,
                    ingredientes_base=producto_original.ingredientes_base.copy(),
                    requiere_horneado=producto_original.requiere_horneado
                )

            # Eliminar el producto antiguo solo si el nombre cambió
            if producto_original.nombre != nombre_limpio:
                del self.cafe.menu[producto_original.nombre]

            # Agregar el producto actualizado (o actualizar el existente si el nombre no cambió)
            self.cafe.menu[nombre_limpio] = producto_actualizado

            # Mostrar mensaje y cerrar diálogo
            messagebox.showinfo("Éxito", "Producto actualizado correctamente")
            if dialog:
                dialog.destroy()

            # Actualizar la vista de administración
            if tree and self.current_admin_frame:
                self._mostrar_admin_productos(self.current_admin_frame)

        except ValueError as e:
            messagebox.showerror("Error de validación", str(e))
        except Exception as e:
            messagebox.showerror("Error inesperado", f"No se pudo actualizar el producto: {str(e)}")
            print(f"Error completo: {traceback.format_exc()}")

    def _eliminar_producto(self, tree):
        """Elimina producto seleccionado"""
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return

        item = tree.item(seleccion[0])
        nombre = item['values'][0]

        if messagebox.askyesno("Confirmar", f"¿Eliminar el producto {nombre}?"):
            try:
                del self.cafe.menu[nombre]
                tree.delete(seleccion[0])
                messagebox.showinfo("Éxito", "Producto eliminado")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {str(e)}")

    def confirmar_pedido(self):
        """Método completo y corregido para confirmar pedidos"""
        try:
            # Verificación básica
            if not hasattr(self, 'productos_pedido') or not self.productos_pedido:
                messagebox.showwarning("Pedido Vacío", "No hay productos en el pedido")
                return

            # Crear el pedido (con ID único automático)
            nuevo_pedido = Pedido(
                cliente=self.usuario_actual,
                productos=self.productos_pedido.copy()
            )

        # Agregar al historial solo si es cliente
            if not hasattr(self.usuario_actual, 'rol') and hasattr(self.usuario_actual, 'historial_pedidos'):
                self.usuario_actual.historial_pedidos.append(nuevo_pedido)

        # Guardar los cambios en el CSV (para clientes)
            if not hasattr(self.usuario_actual, 'rol'):
                self.cafe.guardar_clientes_csv()
            else:
                # Guardar puntos de empleados
                self.cafe.guardar_empleados_csv()

            # Mostrar confirmación mejorada
            self._mostrar_confirmacion(nuevo_pedido)

            # Limpieza final
            self._limpiar_pedido()

        except Exception as e:
            messagebox.showerror("Error", f"Error al confirmar pedido:\n{str(e)}")
            print(f"Error detallado: {e}")  # Log para depuración

    def _mostrar_confirmacion(self, pedido: Pedido):
        """Muestra ventana de confirmación con puntos para todos"""
        confirm_window = tk.Toplevel(self.root)
        confirm_window.title("¡Pedido Exitoso!")
        confirm_window.geometry("400x400")

        # Contenido principal
        main_frame = ttk.Frame(confirm_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Icono de éxito
        ttk.Label(
            main_frame,
            text="✓",
            font=("Arial", 48),
            foreground="green"
        ).pack(pady=10)

        # Detalles del pedido
        detalles = [
            ("N° Pedido:", pedido.id_pedido),
            ("Fecha:", pedido.fecha_creacion.strftime("%d/%m/%Y %H:%M")),
            ("Total:", f"${pedido.total:.2f}"),
            ("Productos:", len(pedido.productos))
        ]

        for texto, valor in detalles:
            frame = ttk.Frame(main_frame)
            frame.pack(fill=tk.X, pady=2)
            ttk.Label(frame, text=texto, width=15, anchor=tk.W).pack(side=tk.LEFT)
            ttk.Label(frame, text=valor, font=("Arial", 10, "bold")).pack(side=tk.LEFT)

        # Mostrar puntos para todos los usuarios
        puntos_frame = ttk.Frame(main_frame, padding=(0, 10))
        puntos_frame.pack(fill=tk.X)

        ttk.Label(
            puntos_frame,
            text=f"Puntos obtenidos: +{pedido.puntos_obtenidos}",
            foreground="blue"
        ).pack(anchor=tk.W)

        ttk.Label(
            puntos_frame,
            text=f"Puntos totales: {self.usuario_actual.puntos_fidelidad}"
        ).pack(anchor=tk.W)

        # Botón de aceptar
        ttk.Button(
            main_frame,
            text="Aceptar",
            command=lambda: [confirm_window.destroy(), self._limpiar_pedido()],
            style='Success.TButton'
        ).pack(pady=15)

        confirm_window.transient(self.root)
        confirm_window.grab_set()
        confirm_window.focus_force()

    def _limpiar_pedido(self):
        """Limpia todos los datos del pedido actual"""
        self.productos_pedido = []

        if hasattr(self, 'pedido_listbox'):
            self.pedido_listbox.delete(0, tk.END)

        if hasattr(self, 'total_pedido'):
            self.total_pedido.set(0.0)
            self.total_str.set("Total: $0.00")

        if hasattr(self, 'promocion_aplicada'):
            self.promocion_aplicada.set("Promoción: Ninguna")

        self.actualizar_puntos_interfaz()
        self.mostrar_menu_principal()
    
    def actualizar_puntos_interfaz(self):
        """
        Actualiza la visualización de puntos de fidelidad en la interfaz
        Versión mejorada con manejo de errores y múltiples estrategias de búsqueda
        """
        try:
            # 1. Verificación de requisitos mínimos
            if not hasattr(self, 'usuario_actual') or not hasattr(self.usuario_actual, 'puntos_fidelidad'):
                return

            puntos = self.usuario_actual.puntos_fidelidad
            texto_puntos = f"Puntos: {puntos}"

            # 2. Intento con referencia directa (método más eficiente)
            if hasattr(self, 'puntos_label_reference'):
                self.puntos_label_reference.config(text=texto_puntos)
                return

            # 3. Búsqueda en la jerarquía de widgets
            if hasattr(self, 'main_frame'):
                for widget in self.main_frame.winfo_children():
                    try:
                        # Verificar si es un Label que muestra puntos
                        if isinstance(widget, (ttk.Label, tk.Label)):
                            current_text = widget.cget('text')  # Uso correcto con 1 argumento

                            # Estrategias para identificar el label de puntos:
                            if (current_text and 
                                (current_text.startswith("Puntos:") or 
                                 "puntos_fidelidad" in str(widget))):
                                widget.config(text=texto_puntos)
                                # Guardar referencia para futuras actualizaciones
                                self.puntos_label_reference = widget
                                break
                    except Exception as e:
                        print(f"Error revisando widget: {str(e)}")
                        continue

            # 4. Actualización alternativa si no se encontró
            if not hasattr(self, 'puntos_label_reference'):
                print("Advertencia: No se encontró el label de puntos en la interfaz")

        except Exception as e:
            print(f"Error crítico en actualizar_puntos_interfaz: {str(e)}")

    def aplicar_promocion_pedido(self):
        """Aplica una promoción al pedido actual"""
        if not self.productos_pedido:
            messagebox.showwarning("Advertencia", "No hay productos en el pedido")
            return

        # Crear un pedido temporal para verificar promociones
        pedido_temp = Pedido(
            cliente=self.usuario_actual,
            productos=self.productos_pedido
        )

        # Buscar promociones aplicables
        promociones_aplicables = [
            p for p in self.cafe.promociones 
            if p.es_aplicable(pedido_temp)
        ]

        if not promociones_aplicables:
            messagebox.showinfo("Promociones", "No hay promociones aplicables")
            return

        # Mostrar diálogo para seleccionar promoción
        dialog = tk.Toplevel(self.root)
        dialog.title("Seleccionar Promoción")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Seleccione una promoción:").pack(pady=10)

        lista_promociones = tk.Listbox(dialog)
        lista_promociones.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        for promocion in promociones_aplicables:
            descripcion = f"{promocion.nombre} - {promocion.descuento_porcentaje}% de descuento"
            if promocion.puntos_requeridos > 0:
                descripcion += f" ({promocion.puntos_requeridos} pts)"
            lista_promociones.insert(tk.END, descripcion)

        # --- AQUÍ VA EL CÓDIGO QUE PREGUNTASTE ---
        def aplicar_seleccion():
            seleccion = lista_promociones.curselection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Seleccione una promoción")
                return

            promocion = promociones_aplicables[seleccion[0]]

            try:
                nuevo_total = promocion.aplicar_descuento(
                    self.total_pedido.get(),
                    self.usuario_actual
                )
                # Actualizar interfaz
                self.total_pedido.set(round(nuevo_total, 2))
                self.total_str.set(f"Total: ${nuevo_total:.2f}")
                self.promocion_aplicada.set(f"Promoción: {promocion.nombre}")
                self.actualizar_puntos_interfaz()  # Actualizar puntos si se usaron

                # Guardar los cambios en el CSV
                self.cafe.guardar_clientes_csv()

                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        # --- FIN DEL CÓDIGO AGREGADO ---

        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)

        ttk.Button(
            button_frame,
            text="Aplicar",
            command=aplicar_seleccion,
            style='Success.TButton'
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Cancelar",
            command=dialog.destroy,
            style='Danger.TButton'
        ).pack(side=tk.LEFT, padx=5)
    
    # -------------------- FUNCIONALIDADES -------------------- #
    def mostrar_menu_completo(self):
        """Muestra el menú completo de la cafetería"""
        self.limpiar_pantalla()
    
        if not self.cafe.menu:
            try:
                self.cafe.inicializar_datos_prueba()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron cargar los productos: {str(e)}")
                self.mostrar_menu_principal()
                return
        
        # Frame principal con scrollbar
        container = ttk.Frame(self.main_frame)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(container, text="Menú Completo", style='Header.TLabel').pack(pady=10)
        
        # Mostrar menú en pestañas
        notebook = ttk.Notebook(container)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Pestaña de Bebidas
        bebidas_frame = ttk.Frame(notebook)
        notebook.add(bebidas_frame, text="Bebidas")
        
        # Sub-pestañas para tipos de bebida
        bebidas_notebook = ttk.Notebook(bebidas_frame)
        bebidas_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Bebidas calientes
        calientes_frame = ttk.Frame(bebidas_notebook)
        bebidas_notebook.add(calientes_frame, text="Calientes")
        self._mostrar_productos_en_frame(
            calientes_frame, 
            lambda p: isinstance(p, Bebida) and getattr(p,'tipo', None)  == TipoBebida.CALIENTE
        )
        
        # Bebidas frías
        frias_frame = ttk.Frame(bebidas_notebook)
        bebidas_notebook.add(frias_frame, text="Fríos")
        self._mostrar_productos_en_frame(
            frias_frame, 
            lambda p: isinstance(p, Bebida) and getattr(p,'tipo', None)  == TipoBebida.FRIA
        )
        
        # Batidos
        batidos_frame = ttk.Frame(bebidas_notebook)
        bebidas_notebook.add(batidos_frame, text="Batidos")
        self._mostrar_productos_en_frame(
            batidos_frame, 
            lambda p: isinstance(p, Bebida) and getattr(p,'tipo', None)  == TipoBebida.BATIDO
        )
        
        # Pestaña de Postres
        postres_frame = ttk.Frame(notebook)
        notebook.add(postres_frame, text="Postres")
        self._mostrar_productos_en_frame(
            postres_frame, 
            lambda p: isinstance(p, Postre)
        )
        
        # Botón para volver
        ttk.Button(
            container,
            text="Volver al Menú Principal",
            command=self.mostrar_menu_principal,
            style='Secondary.TButton'
        ).pack(pady=10)
        
    def _mostrar_historial_pedidos(self):
        """Muestra el historial de pedidos del cliente"""
        if not self.usuario_actual or hasattr(self.usuario_actual, 'rol'):
            messagebox.showerror("Error", " como cliente")
            return
        
        self.limpiar_pantalla()
        
        # Frame principal
        main_frame = ttk.Frame(self.main_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(
            main_frame,
            text="Historial de Pedidos",
            style='Title.TLabel'
        ).pack(pady=10)
        
        # Verificar si hay pedidos
        if not self.usuario_actual.historial_pedidos:
            ttk.Label(
                main_frame,
                text="No tienes pedidos registrados",
                style='Header.TLabel'
            ).pack(pady=20)
        else:
            # Crear Treeview para mostrar los pedidos
            columns = ("#1", "#2", "#3", "#4")
            tree = ttk.Treeview(
                main_frame,
                columns=columns,
                show="headings",
                height=10
            )
            
            # Configurar columnas
            tree.heading("#1", text="Fecha")
            tree.heading("#2", text="Productos")
            tree.heading("#3", text="Total")
            
            tree.column("#1", width=120, anchor=tk.CENTER)
            tree.column("#2", width=200, anchor=tk.W)
            tree.column("#3", width=80, anchor=tk.E)
            
            # Agregar scrollbar
            scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            tree.pack(fill=tk.BOTH, expand=True)
            
            # Llenar con datos
            for pedido in self.usuario_actual.historial_pedidos:
                productos = ", ".join([p.nombre for p in pedido.productos])
                tree.insert("", tk.END, values=(
                    pedido.fecha_creacion.strftime("%Y-%m-%d %H:%M"),
                    productos,
                    f"${pedido.total:.2f}"
                ))
        
        # Botón para volver
        ttk.Button(
            main_frame,
            text="Volver al Menú Principal",
            command=self.mostrar_menu_principal,
            style='Secondary.TButton'
        ).pack(pady=10)

    def _mostrar_productos_en_frame(self, frame, condicion):
        """Muestra los productos que cumplen con la condición en el frame dado"""
        for widget in frame.winfo_children():
            widget.destroy()
 
        # Obtener y verificar productos filtrados
        productos = {}
        for nombre, producto in self.cafe.menu.items():
            try:
                # Verificación adicional para bebidas
                if isinstance(producto, Bebida):
                    if not hasattr(producto, 'tipo') or not isinstance(producto.tipo, TipoBebida):
                        print(f"Advertencia: Bebida '{nombre}' no tiene tipo válido")
                        continue
                
                if condicion(producto):
                    productos[nombre] = producto
            except Exception as e:
                print(f"Error al filtrar producto {nombre}: {str(e)}")
                continue
 
        if not productos:
            ttk.Label(frame, text="No hay productos disponibles en esta categoría").pack()
            return
                

        # Crear un canvas con scrollbar para productos
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mostrar cada producto en un frame separado
        for nombre, producto in productos.items():
            product_frame = ttk.Frame(scrollable_frame, padding=10, relief=tk.RAISED, borderwidth=1)
            product_frame.pack(fill=tk.X, padx=5, pady=5, anchor=tk.W)

            # Información básica del producto
            info_text = f"{producto.nombre} - ${producto.precio_base:.2f}"
            ttk.Label(
                product_frame, 
                text=info_text,
                font=('Arial', 10, 'bold')
            ).pack(anchor=tk.W)

            # Descripción
            ttk.Label(
                product_frame,
                text=producto.descripcion,
                font=('Arial', 9)
            ).pack(anchor=tk.W)

            # Información adicional según el tipo de producto
            if isinstance(producto, Bebida):
                tipo_text = f"Tipo: {producto.tipo.value.capitalize()}"
                tiempo_text = f"Tiempo preparación: {producto.tiempo_preparacion} min"

                ttk.Label(
                    product_frame,
                    text=tipo_text,
                    font=('Arial', 9)
                ).pack(anchor=tk.W)

                ttk.Label(
                    product_frame,
                    text=tiempo_text,
                    font=('Arial', 9)
                ).pack(anchor=tk.W)

            elif isinstance(producto, Postre):
                tags = producto.etiquetas()
                if tags:
                    tags_text = "Etiquetas: " + ", ".join(tags)
                    ttk.Label(
                        product_frame,
                        text=tags_text,
                        font=('Arial', 9)
                    ).pack(anchor=tk.W)

            # Mostrar ingredientes si existen
            if hasattr(producto, 'ingredientes_base') and producto.ingredientes_base:
                ingredientes = ", ".join(f"{k} ({v}g)" if isinstance(v, int) else f"{k} ({v})" 
                                       for k, v in producto.ingredientes_base.items())
                ttk.Label(
                    product_frame,
                    text=f"Ingredientes: {ingredientes}",
                    font=('Arial', 8)
                ).pack(anchor=tk.W)

            # Botón para agregar al pedido (solo para clientes y empleados) 
                ttk.Button(
                    product_frame,
                    text="Agregar al Pedido",
                    command=lambda p=producto: self._agregar_producto(p),
                    style='Success.TButton',
                    width=15
                ).pack(side=tk.RIGHT, padx=5)
    
    def mostrar_realizar_pedido(self):
        """Muestra la interfaz para realizar pedidos (versión corregida)"""
        if not self.usuario_actual:
            messagebox.showerror("Error", "Debes iniciar sesión para realizar un pedido")
            return

        self.limpiar_pantalla()
        self.productos_pedido = []  # Reiniciar lista de productos

        # Inicializar variables esenciales

        self.total_pedido = tk.DoubleVar(value=0.0)  # Corregido el valor inicial (8.0 -> 0.0)
        self.total_str = tk.StringVar(value="Total: $0.00")  # Corregido el valor inicial
        self.promocion_aplicada = tk.StringVar(value="Promoción: Ninguna")  # Corregido nombre y ortografía

        # Frame principal con scrollbar
        container = ttk.Frame(self.main_frame)
        container.pack(fill=tk.BOTH, expand=True)  # Corregido fill-tk.NOTH -> fill=tk.BOTH

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")  # Corregido anchor="no" -> "nw"
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Título
        ttk.Label(  # Corregido tk.label -> ttk.Label
            scrollable_frame,
            text="Realizar Pedido",
            style='Header.TLabel'  # Corregido comillas y nombre del estilo
        ).pack(pady=10)

        # Mostrar menú en pestañas
        notebook = ttk.Notebook(scrollable_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Pestaña de Bebidas
        bebidas_frame = ttk.Frame(notebook)
        notebook.add(bebidas_frame, text="Bebidas")

        # Sub-pestañas para tipos de bebida
        bebidas_notebook = ttk.Notebook(bebidas_frame)
        bebidas_notebook.pack(fill=tk.BOTH, expand=True)

        # Bebidas calientes
        calientes_frame = ttk.Frame(bebidas_notebook)
        bebidas_notebook.add(calientes_frame, text="Calientes")
        self._mostrar_productos_en_frame(calientes_frame, lambda p: isinstance(p, Bebida) and p.tipo == TipoBebida.CALIENTE)

        # Bebidas frías
        frias_frame = ttk.Frame(bebidas_notebook)
        bebidas_notebook.add(frias_frame, text="Fríos")
        self._mostrar_productos_en_frame(frias_frame, lambda p: isinstance(p, Bebida) and p.tipo == TipoBebida.FRIA)

        # Batidos
        batidos_frame = ttk.Frame(bebidas_notebook)
        bebidas_notebook.add(batidos_frame, text="Batidos")
        self._mostrar_productos_en_frame(batidos_frame, lambda p: isinstance(p, Bebida) and p.tipo == TipoBebida.BATIDO)

        # Pestaña de Postres
        postres_frame = ttk.Frame(notebook)
        notebook.add(postres_frame, text="Postres")
        self._mostrar_productos_en_frame(postres_frame, lambda p: isinstance(p, Postre))

        # Lista de productos en el pedido
        ttk.Label(
            scrollable_frame,
            text="Productos en el Pedido:",
            style='Header.TLabel'
        ).pack(pady=10)

        self.pedido_listbox = tk.Listbox(scrollable_frame, height=5)
        self.pedido_listbox.pack(fill=tk.X, padx=10, pady=5)

        # Total y promoción
        ttk.Label(
            scrollable_frame,
            textvariable=self.total_str,
            font=('Arial', 10, 'bold')
        ).pack(pady=5)

        ttk.Label(
            scrollable_frame,
            textvariable=self.promocion_aplicada,
            font=('Arial', 10)
        ).pack(pady=5)

        # Botones de acción
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(pady=10)

        ttk.Button(
            button_frame,
            text="Aplicar Promoción",
            command=self.aplicar_promocion_pedido,
            style='Secondary.TButton'
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Realizar Pedido",
            command=self.confirmar_pedido,
            style='Success.TButton'
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Cancelar",
            command=self.mostrar_menu_principal,
            style='Danger.TButton'
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Eliminar Producto",
            command=self.eliminar_producto_pedido,
            style='Danger.TButton'
        ).pack(side=tk.LEFT, padx=5)
    
    def eliminar_producto_pedido(self):
        """Elimina un producto seleccionado del pedido"""
        try:
            seleccion = self.pedido_listbox.curselection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Debe seleccionar un producto para eliminar")
                return

            indice = seleccion[0]
            producto = self.productos_pedido.pop(indice)
            self.pedido_listbox.delete(indice)

            # Actualizar el total
            self.total_pedido.set(self.total_pedido.get() - producto.precio_final)
            self.total_str.set(f"Total: ${self.total_pedido.get():.2f}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al eliminar el producto: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CafeteriaApp(root)
    root.mainloop()