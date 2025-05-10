#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Detector de Personas con Google Cloud Vision - Versión Simplificada
------------------------------------------------------------------
Este script ha sido simplificado para facilitar la configuración de credenciales.
"""

import os
import sys
import cv2
import io
from google.cloud import vision

# IMPORTANTE: Cambia esta ruta al lugar donde guardaste tu archivo de credenciales
RUTA_CREDENCIALES = r"C:\Users\Jose Carlos\OneDrive\UMG\Tercer semestre\Programacion l\Tareas\Consumo_de_APIs\python\atlantean-wares-449801-c1-c9df0544984f.json"

def main():
    """Función principal del detector simplificado"""
    
    # 1. Configurar las credenciales de Google Cloud
    print(f"Usando archivo de credenciales: {RUTA_CREDENCIALES}")
    if not os.path.exists(RUTA_CREDENCIALES):
        print(f"Error: No se encontró el archivo de credenciales en: {RUTA_CREDENCIALES}")
        print("Edita este script y modifica la variable RUTA_CREDENCIALES.")
        return
    
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = RUTA_CREDENCIALES
    
    # 2. Inicializar el cliente de Vision API
    try:
        vision_client = vision.ImageAnnotatorClient.from_service_account_file(RUTA_CREDENCIALES)
        print("Cliente de Vision API inicializado correctamente.")
    except Exception as e:
        print(f"Error al inicializar Vision API: {e}")
        return
    
    # 3. Capturar imagen de la webcam
    print("\nInicializando cámara web...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: No se pudo acceder a la cámara web.")
        return
    
    print("Cámara inicializada. Presiona ESPACIO para capturar o ESC para salir.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error al leer frame desde la cámara.")
            break
        
        cv2.imshow('Presiona ESPACIO para capturar, ESC para salir', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 32:  # ESPACIO
            cv2.imwrite("captura.jpg", frame)
            print("Imagen capturada y guardada como 'captura.jpg'")
            break
        elif key == 27:  # ESC
            print("Captura cancelada.")
            cap.release()
            cv2.destroyAllWindows()
            return
    
    cap.release()
    cv2.destroyAllWindows()
    
    # 4. Analizar la imagen con Vision API
    print("\nAnalizando imagen con Google Cloud Vision API...")
    
    with io.open("captura.jpg", 'rb') as image_file:
        content = image_file.read()
    
    image = vision.Image(content=content)
    
    # Detectar objetos
    response = vision_client.object_localization(image=image)
    objects = response.localized_object_annotations
    
    # Detectar etiquetas
    label_response = vision_client.label_detection(image=image)
    labels = label_response.label_annotations
    
    # 5. Mostrar resultados
    persona_detectada = False
    for obj in objects:
        if obj.name.lower() in ['person', 'human', 'persona', 'humano']:
            persona_detectada = True
            break
    
    if not persona_detectada:
        for label in labels:
            if label.description.lower() in ['person', 'human', 'persona', 'humano']:
                persona_detectada = True
                break
    
    # Mostrar resultado principal
    if persona_detectada:
        print("\n✅ Persona detectada en la imagen.")
    else:
        print("\n❌ No se detectó ninguna persona en la imagen.")
    
    # Mostrar objetos detectados
    print("\n--- Objetos Detectados ---")
    if objects:
        for i, obj in enumerate(objects, 1):
            print(f"{i}. {obj.name} (Confianza: {obj.score:.2f})")
    else:
        print("No se detectaron objetos.")
    
    # Mostrar etiquetas
    print("\n--- Etiquetas Detectadas ---")
    if labels:
        for i, label in enumerate(labels, 1):
            print(f"{i}. {label.description} (Confianza: {label.score:.2f})")
    else:
        print("No se detectaron etiquetas.")
    
    # 6. Anotar la imagen
    try:
        imagen_original = cv2.imread("captura.jpg")
        altura, ancho, _ = imagen_original.shape
        
        for obj in objects:
            # Color verde para personas, rojo para otros objetos
            color = (0, 255, 0) if obj.name.lower() in ['person', 'human', 'persona', 'humano'] else (0, 0, 255)
            
            box = obj.bounding_poly.normalized_vertices
            x1 = int(box[0].x * ancho)
            y1 = int(box[0].y * altura)
            x2 = int(box[2].x * ancho)
            y2 = int(box[2].y * altura)
            
            cv2.rectangle(imagen_original, (x1, y1), (x2, y2), color, 2)
            cv2.putText(imagen_original, f"{obj.name}: {obj.score:.2f}", 
                        (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        cv2.imwrite("captura_anotada.jpg", imagen_original)
        cv2.imshow("Resultado del Análisis", imagen_original)
        print("\nImagen anotada guardada como 'captura_anotada.jpg'")
        print("Presiona cualquier tecla para finalizar...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    except Exception as e:
        print(f"Error al anotar imagen: {e}")

if __name__ == "__main__":
    main()