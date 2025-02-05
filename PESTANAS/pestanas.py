import tkinter as tk
from tkinter import ttk, messagebox
import serial
import threading
import json
import time
from serial.tools import list_ports

arduino = None
ventana = tk.Tk()
estado = tk.StringVar(value="Sin conexión")
seleccion = tk.StringVar()

ventana.title("Ventana con pestañas")
ventana.geometry("500x300")
ventana.protocol('WM_DELETE_WINDOW', lambda: askQuit())

icono = tk.PhotoImage(file="icon.png")
ventana.iconphoto(True, icono)

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

def actualizar_pestanas():
    if estado.get() == "Conectado":
        nb.tab(1, state="normal")
        nb.tab(2, state="normal")
    else:
        nb.tab(1, state="disabled")
        nb.tab(2, state="disabled")

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

            time.sleep(2)
            arduino.write("Conectado\n".encode())

            actualizar_pestanas()
        except serial.SerialException:
            estado.set("Sin conexión")
            actualizar_estado("red")
            actualizar_pestanas()
    else:
        estado.set("Seleccione un puerto")
        actualizar_estado("red")

def desconectar():
    global arduino
    if arduino and arduino.is_open:
        arduino.close()
        estado.set("Sin conexión")
        actualizar_estado("red")
    
    actualizar_pestanas()

def leer_datos():
    global arduino
    while True:
        try:
            if arduino and arduino.in_waiting > 0:
                data = arduino.readline().decode('utf-8').strip()
                print("Datos recibidos:", data)

                if data.startswith('{') and data.endswith('}'):
                    try:
                        valores = json.loads(data)
                        temp.set(valores.get("tempc", "N/A"))
                        humed.set(valores.get("humed", "N/A"))
                        ldr.set(valores.get("ldr", "N/A"))
                    except json.JSONDecodeError:
                        print("Error al decodificar JSON")
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
            actualizar_color_circulo(int(r), int(g), int(b))
        else:
            messagebox.showerror("Error", "No hay conexión con Arduino")

def actualizar_color_circulo(r, g, b):
    color_hex = f'#{r:02x}{g:02x}{b:02x}'
    canvas_rgb.itemconfig(circulo_rgb, fill=color_hex)

nb = ttk.Notebook(ventana)
nb.pack(fill='both', expand=True)

p1 = ttk.Frame(nb)
p2 = ttk.Frame(nb)
p3 = ttk.Frame(nb)

nb.add(p1, text=' Conexión ')
nb.add(p2, text=' Lectura DHT11 & LDR ')
nb.add(p3, text=' Escritura RGB ')

nb.tab(1, state="disabled")
nb.tab(2, state="disabled")

selector = ttk.Combobox(p1, state="readonly", textvariable=seleccion)
selector.pack(pady=10)

canvas = tk.Canvas(p1, width=80, height=80)
canvas.place(x=300, y=75)
estado_circulo = canvas.create_oval(5, 5, 75, 75, fill="red")

boton_conectar = tk.Button(p1, text="Conectar", command=conectar)
boton_conectar.place(x=30, y=100)

boton_desconectar = tk.Button(p1, text="Desconectar", command=desconectar)
boton_desconectar.place(x=150, y=100)

tk.Label(p2, text="Temperatura C:").pack()
tk.Entry(p2, textvariable=temp, state="readonly").pack()

tk.Label(p2, text="Humedad:").pack()
tk.Entry(p2, textvariable=humed, state="readonly").pack()

tk.Label(p2, text="Intensidad LDR:").pack()
tk.Entry(p2, textvariable=ldr, state="readonly").pack()

tk.Label(p3, text="R:").pack()
entrada_r = tk.Entry(p3)
entrada_r.pack()

tk.Label(p3, text="G:").pack()
entrada_g = tk.Entry(p3)
entrada_g.pack()

tk.Label(p3, text="B:").pack()
entrada_b = tk.Entry(p3)
entrada_b.pack()

canvas_rgb = tk.Canvas(p3, width=80, height=80)
canvas_rgb.place(x=350, y=60)
circulo_rgb = canvas_rgb.create_oval(5, 5, 75, 75, fill="black")

boton_rgb = tk.Button(p3, text="Enviar", command=enviar_rgb)
boton_rgb.pack()

hilo_serial = threading.Thread(target=leer_datos, daemon=True)
hilo_serial.start()

mostrar()
ventana.mainloop()