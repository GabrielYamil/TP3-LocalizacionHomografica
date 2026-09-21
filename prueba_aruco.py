import cv2

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

    cv2.imshow("Cam", frame)

    tecla = cv2.waitKey(1) & 0xFF

    if tecla == ord('r'):

        if ids is None:
            print("No se puede registrar: no hay ningun aruco registrado.")
        
        else:
            indice = 0

            id_registrado = int(ids[indice])

            esquinas_registradas = esquinas[indice][0].copy()

            print("\n==============================")
            print("REGISTRO REALIZADO")
            print("==============================")
            print(f"ID registrado: {id_registrado}")

            for i, punto in enumerate(esquinas_registradas):
                x, y = punto
                print(f"Esquina {i}: ({x:.1f}, {y:.1f})")
            
            print("==============================\n")


    if tecla == 27:
        break

camara.release()
cv2.destroyAllWindows()