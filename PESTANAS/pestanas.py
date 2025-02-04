import tkinter as tk
from tkinter import ttk, messagebox
import serial
import threading
from serial.tools import list_ports

arduino = None
ventana = tk.Tk()
estado = tk.StringVar(value="Sin conexión")
seleccion = tk.StringVar()

# Ventana principal
ventana.title("Ventana con pestañas")
ventana.geometry("500x300")
ventana.protocol('WM_DELETE_WINDOW', lambda: askQuit())

temp = tk.StringVar()
humed = tk.StringVar()
ldr = tk.StringVar()

def askQuit():
    global arduino
    if arduino and arduino.is_open:
        arduino.close()
    ventana.destroy()

def puertos():
    return [port.device for port in list_ports.comports()]

def mostrar():
    selector['values'] = puertos()

def actualizar_estado(color):
    canvas.itemconfig(estado_circulo, fill=color)

def conectar():
    global arduino
    seleccion_puerto = selector.get()
    
    if seleccion_puerto:
        try:
            estado.set("Conectando...")
            actualizar_estado("yellow")
            ventana.update_idletasks()

            arduino = serial.Serial(seleccion_puerto, 9600, timeout=1)
            estado.set("Conectado")
            actualizar_estado("green")
            arduino.write(b"Conectado\n")
        except serial.SerialException:
            estado.set("Sin conexión")
            actualizar_estado("red")
    else:
        estado.set("Seleccione un puerto")
        actualizar_estado("red")

def desconectar():
    global arduino
    if arduino and arduino.is_open:
        arduino.close()
        estado.set("Sin conexión")
        actualizar_estado("red")
    else:
        estado.set("No hay conexión")
        actualizar_estado("red")

def comprobar_conexion():
    global arduino
    if arduino and arduino.is_open:
        arduino.write(b"Comprobar\n")
        respuesta = arduino.readline().decode().strip()
        if respuesta == "CONECTADO":
            estado.set("Conectado")
            actualizar_estado("green")
        else:
            estado.set("Sin conexión")
            actualizar_estado("red")
    else:
        estado.set("Sin conexión")
        actualizar_estado("red")

def leer_datos():
    global arduino
    while True:
        try:
            if arduino and arduino.in_waiting > 0:
                data = arduino.readline().decode('utf-8').strip()
                print("Datos recibidos:", data)
                if data.startswith('{') and data.endswith('}'):
                    valores = eval(data)
                    temp.set(valores.get("tempC", "N/A"))
                    humed.set(valores.get("humed", "N/A"))
                    ldr.set(valores.get("LDR", "N/A"))
        except Exception as e:
            print("Error leyendo datos:", e)
            break

def comprobacion(valor):
    try:
        valor = int(valor)
        if 0 <= valor <= 255:
            return True
        else:
            messagebox.showerror(message=f"El valor {valor} está fuera del rango (0-255).", title="ERROR")
            return False
    except ValueError:
        messagebox.showerror(message="Introducir valores válidos.", title="ERROR")
        return False

def enviar_rgb():
    global arduino
    r = entrada_r.get()
    g = entrada_g.get()
    b = entrada_b.get()
    
    if comprobacion(r) and comprobacion(g) and comprobacion(b):
        cadenaRGB = f'{{"r":{r},"g":{g},"b":{b}}}'
        print("Enviando:", cadenaRGB)
        if arduino and arduino.is_open:
            arduino.write(cadenaRGB.encode('utf-8'))
        else:
            messagebox.showerror("Error", "No hay conexión con Arduino")

nb = ttk.Notebook(ventana)
nb.pack(fill='both', expand=True)

p1 = ttk.Frame(nb)
p2 = ttk.Frame(nb)
p3 = ttk.Frame(nb)

nb.add(p1, text=' Conexión ')
nb.add(p2, text=' Lectura DHT11 & LDR ')
nb.add(p3, text=' Escritura RGB ')

# Contenido de la pestaña 1 (Conexión)
selector = ttk.Combobox(p1, state="readonly", textvariable=seleccion)
selector.pack(pady=10)

canvas = tk.Canvas(p1, width=80, height=80)
canvas.place(x=300, y=75)
estado_circulo = canvas.create_oval(5, 5, 75, 75, fill="red")

boton_conectar = tk.Button(p1, text="Conectar", command=conectar)
boton_conectar.place(x=30, y=100)

boton_desconectar = tk.Button(p1, text="Desconectar", command=desconectar)
boton_desconectar.place(x=150, y=100)

# Contenido de la pestaña 2 (Lectura DHT11 & LDR)
tk.Label(p2, text="Temperatura C:").pack()
tk.Entry(p2, textvariable=temp, state="readonly").pack()

tk.Label(p2, text="Humedad:").pack()
tk.Entry(p2, textvariable=humed, state="readonly").pack()

tk.Label(p2, text="Intensidad LDR:").pack()
tk.Entry(p2, textvariable=ldr, state="readonly").pack()

# Contenido de la pestaña 3 (Envío de datos RGB)
tk.Label(p3, text="R:").pack()
entrada_r = tk.Entry(p3)
entrada_r.pack()

tk.Label(p3, text="G:").pack()
entrada_g = tk.Entry(p3)
entrada_g.pack()

tk.Label(p3, text="B:").pack()
entrada_b = tk.Entry(p3)
entrada_b.pack()

canvas = tk.Canvas(p3, width=80, height=80)
canvas.place(x=350, y=60)
estado_circulo = canvas.create_oval(5, 5, 75, 75, fill="red")

boton_rgb = tk.Button(p3, text="Enviar", command=enviar_rgb)
boton_rgb.pack()

hilo_serial = threading.Thread(target=leer_datos, daemon=True)
hilo_serial.start()

mostrar()
ventana.mainloop()