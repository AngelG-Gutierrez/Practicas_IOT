import tkinter as tk
from tkinter import messagebox
import serial
import threading
#import json
arduino = serial.Serial('/dev/tty.usbmodem1401',9600)
ventana = tk.Tk() # Crear la ventana principal
valor = 0

temp = tk.StringVar()
humed = tk.StringVar()
ldr = tk.StringVar()

#if arduinoDHT.strip():
   # print("tempC:",json_object["tempC"])
    #print("humed:",json_object["humed"])
    #print("LDR:",json_object["LDR"])               

def comprobacion(valor):
    try:
        valor = int(valor)
        if 0 <= valor <= 255:
            return True
        else:
            messagebox.showerror(message=f"El valor {valor} está fuera del rango (0-255).", title="ERROR")
            return False
    except ValueError:
        messagebox.showerror(message=f"Introducir valores", title="ERROR")
        return False

def funcion():
    cadena1 = entrada1.get()
    cadena2 = entrada2.get()
    cadena3 = entrada3.get()
    
    if comprobacion(cadena1) and comprobacion(cadena2) and comprobacion(cadena3):
        cadenaRGB = f'{{"r":{cadena1},"g":{cadena2},"b":{cadena3}}}'
        print("CADENA RGB:", cadenaRGB)
        arduino.write(cadenaRGB.encode('utf-8'))
    else:
        print("Corrige los valores antes de continuar.")

def leer_datos():
    while True:
        try:
            if arduino.in_waiting > 0:
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

def askQuit():
    ventana.destroy()
    arduino.close()
    hilo_serial.join()

    #cerrar conexion

ventana.geometry("300x400")     # Dimensiones
ventana.title("Led RGB") # Titulo
ventana.protocol('WM_DELETE_WINDOW',askQuit)
        
etiqueta1 = tk.Label(ventana, text="R:")   # Etiqueta
etiqueta1.pack()                                 # Agregar etiqueta
entrada1 = tk.Entry(ventana)                     # Caja de texto
entrada1.pack()                            # Agregar caja de texto

etiqueta2 = tk.Label(ventana, text="G:")   # Etiqueta
etiqueta2.pack()                                 # Agregar etiqueta
entrada2 = tk.Entry(ventana)                     # Caja de texto
entrada2.pack()                                  # Agregar caja de texto

etiqueta3 = tk.Label(ventana, text="B:")   # Etiqueta
etiqueta3.pack()                                 # Agregar etiqueta
entrada3 = tk.Entry(ventana)                     # Caja de texto
entrada3.pack()                            # Agregar caja de texto


boton_confirmar = tk.Button(ventana, text="Aceptar", command=funcion)   # Botón
                                                                        # Asiganción de botón
boton_confirmar.pack()                                                  # Agregar botón

salto = tk.Entry(ventana,state="disabled")
salto.pack()

#sensor de humedad

tk.Label(ventana, text="Temperatura C:").pack()
entrada4 = tk.Entry(ventana, textvariable=temp, state="readonly")
entrada4.pack()

tk.Label(ventana, text="Humedad:").pack()
entrada5 = tk.Entry(ventana, textvariable=humed, state="readonly")
entrada5.pack()

tk.Label(ventana, text="Intensidad:").pack()
entrada6 = tk.Entry(ventana, textvariable=ldr, state="readonly")
entrada6.pack()

# Iniciar el hilo de lectura
hilo_serial = threading.Thread(target=leer_datos, daemon=True)
hilo_serial.start()


ventana.mainloop()            # Iniciar la ventana
