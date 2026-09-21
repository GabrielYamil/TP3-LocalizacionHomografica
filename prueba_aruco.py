import cv2
import numpy as np

diccionario = cv2.aruco.getPredefinedDictionary(
    cv2.aruco.DICT_4X4_50
)

parametros = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(diccionario, parametros)

camara = cv2.VideoCapture(1)

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

while True:

    ret, frame = camara.read()
    
    if not ret:
        print("No se pudo leer el frame de la cámara")
        break

    # Detectar marcadores ArUco en el frame
    esquinas, ids, rechazados = detector.detectMarkers(frame)

    # Dibujar los marcadores detectados en el frame
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

    if homografia_metrica is not None and ids is not None:
        
        indice_actual = None

        for i, id_actual in enumerate(ids):
            if int(id_actual) == id_registrado:
                indice_actual = i
                break
        
        if indice_actual is not None:

            esquinas_actuales = esquinas[indice_actual][0]

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


            texto = (
                f"X: {x_actual:.1f} mm  "
                f"Y: {y_actual:.1f} mm  "
                f"Angulo: {angulo:.1f} grados"
            )

            cv2.putText(frame,
                        texto, (20, 35),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 0), 
                        2
                    )

    cv2.imshow("Camara", frame)


    if tecla == 27:
        break

camara.release()
cv2.destroyAllWindows()