# Trabajo Práctico 3: Localización Homográfica
## Visión Artificial — Universidad Nacional de La Matanza (UNLaM)

Este proyecto implementa un sistema de **localización métrica bidimensional en tiempo real** utilizando marcadores **ArUco** y estimación de **homografía plana**. A partir de la detección de un marcador ArUco en una secuencia de video, el sistema permite registrar un plano métrico y estimar la posición $(X, Y)$ en milímetros y la rotación (en grados) del marcador respecto al origen del mundo real.

---

## 🛠️ Requisitos del Sistema

El proyecto está desarrollado en Python y utiliza las siguientes librerías:
*   **NumPy** (procesamiento matricial y vectorial)
*   **OpenCV** con soporte de contrib (`opencv-contrib-python`), necesario para el módulo `cv2.aruco`.

Las versiones exactas recomendadas se encuentran en `requirements.txt`:
```text
numpy==2.5.3
opencv-contrib-python==5.0.0.93
```

---

## 🚀 Instalación y Configuración

1. **Clonar o situarse en el directorio del proyecto:**
   ```bash
   cd TP3-LocalizacionHomografica
   ```

2. **Crear y activar un entorno virtual (opcional pero recomendado):**
   * En macOS/Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   * En Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```

3. **Instalar las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 📂 Estructura del Proyecto

*   `generar_aruco.py`: Script para crear y exportar un marcador ArUco personalizado.
*   `prueba_aruco.py`: Script principal de detección, calibración homográfica y localización en tiempo real mediante cámara.
*   `requirements.txt`: Archivo de dependencias del proyecto.
*   `aruco_id0.png`: Imagen del marcador ArUco generado con ID 0.

---

## 📖 Instrucciones de Uso

### 1. Generar el Marcador ArUco
Si necesitas imprimir o visualizar el marcador ArUco en pantalla, puedes ejecutar:
```bash
python generar_aruco.py
```
Este script utiliza el diccionario `DICT_4X4_50` para generar un marcador con el **ID 0** de $1000 \times 1000$ píxeles y guardarlo como `maruco_id0.png`.

### 2. Ejecutar la Localización Homográfica
Para iniciar la captura de video y realizar la detección:
```bash
python prueba_aruco.py
```

> **Nota:** Por defecto, el script intenta abrir el dispositivo de cámara en el índice `1` (`cv2.VideoCapture(1)`). Si tu cámara integrada o USB principal está en otro índice (como el predeterminado `0`), edita la línea `camara = cv2.VideoCapture(1)` en `prueba_aruco.py` según corresponda.

### 3. Registro del Plano Métrico
Una vez que el marcador ArUco sea visible y detectado por la cámara:
1. Sostén o posiciona el marcador en un plano estable frente a la cámara.
2. Presiona la tecla **`R`** (en mayúscula o minúscula) para realizar el **registro homográfico**.
3. El script calculará la matriz de homografía que mapea las esquinas del marcador en la imagen a coordenadas métricas reales (definidas como un cuadrado de $100 \times 100\text{ mm}$ en el espacio del mundo).
4. La consola imprimirá:
   * Las esquinas del ArUco transformadas a milímetros.
   * La coordenada del centro del marcador respecto al origen del mundo.
   * La matriz de homografía resultante ($3 \times 3$).

### 4. Seguimiento en Tiempo Real
Una vez registrado, puedes mover el marcador libremente por el plano de la cámara. El sistema proyectará su posición sobre el frame mostrando en la esquina superior izquierda de la pantalla:
*   **X (mm)**: Posición horizontal en milímetros en el plano de calibración.
*   **Y (mm)**: Posición vertical en milímetros en el plano de calibración.
*   **Ángulo (grados)**: Rotación sobre el plano.

Además, **se abrirá automáticamente una nueva ventana llamada "Vista Cenital W2D"**, que muestra en tiempo real la proyección de la escena rectificada a un plano cenital y perpendicular de $500 \times 500$ píxeles. En esta vista cenital, el marcador ArUco se observará centrado, estático y corregido de toda perspectiva tridimensional.

Para salir del programa, presiona la tecla **`ESC`**.

---

## 🔬 Detalles de la Implementación Matemática

### Estimación de Homografía
La homografía plana relaciona los puntos del plano de la imagen $\mathbf{p}_i = [x_i, y_i, 1]^T$ con los puntos correspondientes en el plano métrico del mundo $\mathbf{p}_w = [X_w, Y_w, 1]^T$ mediante una matriz proyectiva $H$ de $3 \times 3$:

$$\mathbf{p}_w \sim H \mathbf{p}_i$$

En `prueba_aruco.py`, cuando se presiona `R`, se definen las esquinas de destino en milímetros correspondientes a un marcador de $100\text{ mm} \times 100\text{ mm}$:
```python
puntos_mundo = np.array([
    [0, 100],    # Esquina superior izquierda (0, 100) mm
    [100, 100],  # Esquina superior derecha (100, 100) mm
    [100, 0],    # Esquina inferior derecha (100, 0) mm
    [0, 0]       # Esquina inferior izquierda (0, 0) mm
], dtype=np.float32)
```

La matriz de homografía $H$ es calculada con `cv2.findHomography(esquinas_registradas, puntos_mundo)`.

### Localización del Centro y Cálculo de Rotación
Para cada frame subsiguiente, las esquinas del ArUco detectadas se proyectan al plano métrico usando $H$ mediante `cv2.perspectiveTransform()`.

1. **Centro métrico ($X_c, Y_c$):** Se calcula como la media aritmética de las cuatro esquinas proyectadas en el plano del mundo.
2. **Ángulo de rotación ($\theta$):** Se estima calculando el arcotangente de la diferencia de coordenadas entre la esquina 1 y la esquina 0 proyectadas:
   $$\theta = \arctan2(\Delta Y, \Delta X) \times \frac{180}{\pi}$$
   Esto proporciona la orientación del marcador en grados respecto al eje de referencia del plano métrico calibrado.
