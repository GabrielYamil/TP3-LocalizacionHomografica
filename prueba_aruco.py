import cv2
import numpy as np

diccionario = cv2.aruco.getPredefinedDictionary(
    cv2.aruco.DICT_4X4_50
)

parametros = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(diccionario, parametros)

camara = cv2.VideoCapture(0)

if not camara.isOpened():
    print("No se pudo abrir la cámara")
    exit()

print("Camara iniciada.")
print("Mostrar un marcador ArUco frente a la camara.")
print("Presionar R para mostrar el plano.")
print("Presiona ESC para salir.")

esquinas_registradas = None
id_registrado = None
homografia_metrica = None
homografia_cenital = None
fondo_cenital = None

while True:

    ret, frame = camara.read()
    
    if not ret:
        print("No se pudo leer el frame de la cámara")
        break

    # Hacer una copia del frame limpio para el registro de fondo no vivo
    frame_limpio = frame.copy()

    # Detectar marcadores ArUco en el frame
    esquinas, ids, rechazados = detector.detectMarkers(frame)

    # Dibujar los marcadores detectados en el frame (solo para la ventana de cámara Cam)
    if ids is not None:
        cv2.aruco.drawDetectedMarkers(frame, esquinas, ids)


    tecla = cv2.waitKey(1) & 0xFF

    if tecla == ord('r'):

        if ids is None:
            print("No se puede registrar: no hay ningun aruco registrado.")
        
        else:
            indice = 0

            id_registrado = int(ids[indice])

            esquinas_registradas = esquinas[indice][0].copy()

            puntos_mundo = np.array([
                [0, 100],
                [100, 100],
                [100, 0],
                [0, 0]
            ], dtype=np.float32)

            homografia_metrica, _ = cv2.findHomography(esquinas_registradas, puntos_mundo)

            puntos_transformados = cv2.perspectiveTransform(esquinas_registradas.reshape(-1, 1, 2), homografia_metrica)
            puntos_transformados = puntos_transformados.reshape(-1, 2)

            # Calcular homografía para la visualización de la vista cenital W2D (lienzo de 500x500 px)
            puntos_destino_cenital = np.array([
                [150, 150],  # Esquina 0 (superior izquierda)
                [350, 150],  # Esquina 1 (superior derecha)
                [350, 350],  # Esquina 2 (inferior derecha)
                [150, 350]   # Esquina 3 (inferior izquierda)
            ], dtype=np.float32)
            homografia_cenital, _ = cv2.findHomography(esquinas_registradas, puntos_destino_cenital)

            # Generar el fondo cenital estático (no vivo) una única vez en este instante discreto
            fondo_cenital = cv2.warpPerspective(frame_limpio, homografia_cenital, (500, 500))

            print("\nEsquinas transformadas a mm:")
            for i, punto in enumerate(puntos_transformados):
                x, y = punto
                print(f"Esquina {i}: ({x:.1f}, {y:.1f})")

            centro_mundo = np.mean(puntos_transformados, axis=0)

            print("\nCentro del ArUco en el mundo:")
            print(f"X = {centro_mundo[0]:.2f} mm")
            print(f"Y = {centro_mundo[1]:.2f} mm")

            print("\n==============================")
            print("REGISTRO REALIZADO")
            print("==============================")
            print(f"ID registrado: {id_registrado}")
            
            print("\nHomografia imagen -> mm:")
            print(homografia_metrica)
            print("==============================\n")

    # Inicializar banderas de seguimiento y datos métricos para la ventana Cam y W2D
    marcador_detectado = False
    x_actual, y_actual, angulo = 0.0, 0.0, 0.0
    esquinas_actuales = None

    if homografia_metrica is not None and ids is not None:
        indice_actual = None
        for i, id_actual in enumerate(ids):
            if int(id_actual) == id_registrado:
                indice_actual = i
                break
        
        if indice_actual is not None:
            marcador_detectado = True
            esquinas_actuales = esquinas[indice_actual][0]

            # Calcular pose real en milímetros
            puntos_mundo_actuales = cv2.perspectiveTransform(esquinas_actuales.reshape(-1, 1, 2), homografia_metrica)
            puntos_mundo_actuales = puntos_mundo_actuales.reshape(-1, 2)

            centro_mundo_actual = np.mean(puntos_mundo_actuales, axis=0)
            x_actual = centro_mundo_actual[0]
            y_actual = centro_mundo_actual[1]

            esquina_0 = puntos_mundo_actuales[0]
            esquina_1 = puntos_mundo_actuales[1]

            dx = esquina_1[0] - esquina_0[0]
            dy = esquina_1[1] - esquina_0[1]
            angulo = np.degrees(np.arctan2(dy, dx))

            # Dibujar etiqueta de localización métrica en el feed de la cámara (Cam)
            texto_cam = f"X: {x_actual:.1f} mm  Y: {y_actual:.1f} mm  Angulo: {angulo:.1f} grados"
            cv2.putText(frame, texto_cam, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

    # Gestión de la ventana cenital W2D
    if fondo_cenital is not None:
        # Partimos del fondo estático capturado discrecionalmente durante el registro
        imagen_cenital = fondo_cenital.copy()

        # Dibujar siempre los sistemas de coordenadas para orientación visual
        # 1. Ejes de Referencia del Mundo (Origen en la esquina 3 del marcador registrado en [150, 350] px)
        orig_ref = (150, 350)
        fin_x_ref = (250, 350)
        fin_y_ref = (150, 250)
        # Eje X de referencia en Rojo
        cv2.arrowedLine(imagen_cenital, orig_ref, fin_x_ref, (0, 0, 255), 2, tipLength=0.15)
        cv2.putText(imagen_cenital, "X", (255, 355), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1, cv2.LINE_AA)
        # Eje Y de referencia en Verde
        cv2.arrowedLine(imagen_cenital, orig_ref, fin_y_ref, (0, 255, 0), 2, tipLength=0.15)
        cv2.putText(imagen_cenital, "Y", (145, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1, cv2.LINE_AA)
        # Etiqueta de origen
        cv2.putText(imagen_cenital, "O(0,0)", (115, 365), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)

        # 2. Ejes canónicos de la imagen cenital (Origen en el centro exacto [250, 250] px)
        orig_can = (250, 250)
        fin_x_can = (320, 250)
        fin_y_can = (250, 180)
        # Eje X canónico en Cian
        cv2.arrowedLine(imagen_cenital, orig_can, fin_x_can, (255, 255, 0), 1, tipLength=0.15)
        cv2.putText(imagen_cenital, "Xc", (325, 255), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1, cv2.LINE_AA)
        # Eje Y canónico en Amarillo
        cv2.arrowedLine(imagen_cenital, orig_can, fin_y_can, (0, 255, 255), 1, tipLength=0.15)
        cv2.putText(imagen_cenital, "Yc", (245, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1, cv2.LINE_AA)
        # Punto del centro de la imagen
        cv2.circle(imagen_cenital, orig_can, 2, (255, 255, 255), -1)

        # Si el marcador registrado es visible, dibujar los overlays dinámicos correspondientes
        if marcador_detectado and esquinas_actuales is not None:
            # Proyectar las esquinas de cámara al espacio cenital usando homografia_cenital
            esquinas_w2d = cv2.perspectiveTransform(esquinas_actuales.reshape(-1, 1, 2), homografia_cenital).reshape(-1, 2)
            
            # 1. Dibujar el contorno cuadrado del marcador fiduciario en W2D
            puntos_poligono = esquinas_w2d.astype(np.int32).reshape((-1, 1, 2))
            cv2.polylines(imagen_cenital, [puntos_poligono], isClosed=True, color=(255, 255, 0), thickness=2)

            # 2. Dibujar flecha indicando localización y orientación
            # Centro geométrico del marcador en píxeles W2D
            centro_w2d = np.mean(esquinas_w2d, axis=0).astype(int)
            # Frente del marcador (punto medio del borde superior, esquinas 0 y 1)
            frente_w2d = np.mean(esquinas_w2d[0:2], axis=0).astype(int)
            # Dibujar la flecha en color Azul en BGR (255, 0, 0)
            cv2.arrowedLine(imagen_cenital, tuple(centro_w2d), tuple(frente_w2d), color=(255, 0, 0), thickness=3, tipLength=0.25)

            # 3. Dibujar etiquetas dinámicas con coordenadas reales y orientación
            txt_coord = f"Pose: ({x_actual:.1f}, {y_actual:.1f}) mm"
            txt_ang = f"Angulo: {angulo:.1f} grados"
            cv2.putText(imagen_cenital, txt_coord, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(imagen_cenital, txt_ang, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
        else:
            # Avisar visualmente si se ha perdido el seguimiento del marcador registrado
            cv2.putText(imagen_cenital, "Marcador no detectado", (140, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

        # Mostrar la ventana cenital W2D
        cv2.imshow("W2D", imagen_cenital)

    # Mostrar la ventana de la cámara principal Cam
    cv2.imshow("Cam", frame)

    if tecla == 27:
        break

camara.release()
cv2.destroyAllWindows()