from flask import Flask, request, redirect, url_for, render_template, send_from_directory  # Importa módulos de Flask para crear la aplicación web y manejar solicitudes, redirecciones, URLs, plantillas y envío de archivos.
import os  # Importa el módulo os para interactuar con el sistema operativo.
import cv2  # Importa OpenCV para la manipulación de imágenes.
import easyocr  # Importa easyocr para el reconocimiento óptico de caracteres.

app = Flask(__name__)  # Crea una instancia de la aplicación Flask.
UPLOAD_FOLDER = 'uploads'  # Define la carpeta donde se almacenarán los archivos subidos.
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Configura la aplicación Flask para usar la carpeta de subidas definida.

reader = easyocr.Reader(["es"], gpu=False)  # Inicializa el lector OCR de easyocr para el idioma español sin usar GPU.

@app.route('/')  # Define la ruta para la página de inicio.
def upload_form():
    return render_template('upload.html')  # Renderiza la plantilla 'upload.html' cuando se accede a la página de inicio.

@app.route('/', methods=['POST'])  # Define la ruta para manejar solicitudes POST en la página de inicio.
def upload_image():
    if 'file' not in request.files:  # Verifica si no hay archivo en la solicitud.
        return redirect(request.url)  # Redirige a la misma URL si no hay archivo.
    file = request.files['file']  # Obtiene el archivo de la solicitud.
    if file.filename == '':  # Verifica si el nombre del archivo está vacío.
        return redirect(request.url)  # Redirige a la misma URL si el nombre del archivo está vacío.
    if file:  # Si hay un archivo:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)  # Construye la ruta completa para guardar el archivo.
        file.save(file_path)  # Guarda el archivo en la ruta especificada.
        return redirect(url_for('display_image', filename=file.filename))  # Redirige a la URL de visualización de la imagen con el nombre del archivo como parámetro.

@app.route('/display/<filename>')  # Define la ruta para mostrar la imagen procesada.
def display_image(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Construye la ruta completa de la imagen subida.
    image = cv2.imread(file_path)  # Lee la imagen usando OpenCV.
    result = reader.readtext(image, paragraph=False)  # Realiza OCR en la imagen y obtiene el texto encontrado.

    for res in result:  # Itera sobre los resultados del OCR.
        pt0 = tuple(map(int, res[0][0]))  # Convierte las coordenadas del primer punto en enteros.
        pt1 = tuple(map(int, res[0][1]))  # Convierte las coordenadas del segundo punto en enteros.
        pt2 = tuple(map(int, res[0][2]))  # Convierte las coordenadas del tercer punto en enteros.
        pt3 = tuple(map(int, res[0][3]))  # Convierte las coordenadas del cuarto punto en enteros.

        cv2.rectangle(image, pt0, (pt1[0], pt1[1] - 23), (166, 56, 242), -1)  # Dibuja un rectángulo relleno en la imagen.
        cv2.putText(image, res[1], (pt0[0], pt0[1] - 3), 2, 0.8, (255, 255, 255), 1)  # Añade el texto reconocido en la imagen.

        cv2.rectangle(image, pt0, pt2, (166, 56, 242), 2)  # Dibuja un rectángulo alrededor del texto reconocido.
        cv2.circle(image, pt0, 2, (255, 0, 0), 2)  # Dibuja un círculo en el primer punto.
        cv2.circle(image, pt1, 2, (0, 255, 0), 2)  # Dibuja un círculo en el segundo punto.
        cv2.circle(image, pt2, 2, (0, 0, 255), 2)  # Dibuja un círculo en el tercer punto.
        cv2.circle(image, pt3, 2, (0, 255, 255), 2)  # Dibuja un círculo en el cuarto punto.

    result_image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"result_{filename}")  # Construye la ruta para la imagen resultante.
    cv2.imwrite(result_image_path, image)  # Guarda la imagen resultante en la ruta especificada.
    return send_from_directory(app.config['UPLOAD_FOLDER'], f"result_{filename}")  # Envía la imagen resultante desde la carpeta de subidas.

if __name__ == "__main__":  # Comprueba si el script se está ejecutando directamente.
    if not os.path.exists(UPLOAD_FOLDER):  # Verifica si la carpeta de subidas no existe.
        os.makedirs(UPLOAD_FOLDER)  # Crea la carpeta de subidas si no existe.
    app.run(debug=True)  # Inicia la aplicación Flask en modo debug.
