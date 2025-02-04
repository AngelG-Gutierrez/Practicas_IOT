import tkinter as tk
from tkinter import ttk
import serial
from serial.tools import list_ports

arduino = None  
ventana = tk.Tk()
estado = tk.StringVar(value="Sin conexión")
seleccion = tk.StringVar()

def askQuit():
    global arduino
    if arduino and arduino.is_open:
        arduino.close()
    ventana.destroy()

def puertos():
    return [port.device for port in list_ports.comports()]

def mostrar():
    selector['values'] = puertos()

def conectar():
    global arduino
    seleccion_puerto = selector.get()
    
    if seleccion_puerto:
        try:
            estado.set("Conectando...")
            status.config(fg="blue")
            ventana.update_idletasks()

            arduino = serial.Serial(seleccion_puerto, 9600, timeout=1)
            estado.set("Conectado")
            status.config(fg="green")  
            
            arduino.write(b"Conectado\n")
        except serial.SerialException:
            estado.set("Sin conexión")
            status.config(fg="red")
    else:
        estado.set("Seleccione un puerto")
        status.config(fg="red")

# Función para desconectar Arduino
def desconectar():
    global arduino
    if arduino and arduino.is_open:
        arduino.close()
        estado.set("Sin conexión")
        status.config(fg="red")
    else:
        estado.set("No hay conexión")
        status.config(fg="red")

# Función para comprobar la conexión
def comprobar_conexion():
    global arduino
    if arduino and arduino.is_open:
        arduino.write(b"Comprobar\n")
        respuesta = arduino.readline().decode().strip()
        if respuesta == "CONECTADO":
            estado.set("Conectado")
            status.config(fg="green")
        else:
            estado.set("Sin conexión")
            status.config(fg="red")
    else:
        estado.set("Sin conexión")
        status.config(fg="red")

ventana.geometry("300x200")
ventana.title("Conexión Arduino")
ventana.protocol('WM_DELETE_WINDOW', askQuit)

icono = tk.PhotoImage(file="icon.png")
ventana.iconphoto(True, icono)

selector = ttk.Combobox(ventana, state="readonly", textvariable=seleccion)
selector.pack(pady=10)

boton_conectar = tk.Button(ventana, text="Conectar", command=conectar)
boton_conectar.place(x=30, y=50)

boton_desconectar = tk.Button(ventana, text="Desconectar", command=desconectar)
boton_desconectar.place(x=150, y=50)

boton_comprobar = tk.Button(ventana, text="Comprobar", command=comprobar_conexion)
boton_comprobar.place(x=90, y=100)

status = tk.Label(ventana, textvariable=estado, fg="red", justify="center")
status.place(x=50, y=150, width=200)

mostrar()

ventana.mainloop()