import cv2

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
print("Presiona ESC para salir.")

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

    # Mostrar el frame con los marcadores detectados
    cv2.imshow("Cam", frame)

    # Salir si se presiona la tecla ESC
    tecla = cv2.waitKey(1) & 0xFF

    if tecla == 27:
        break

camara.release()
cv2.destroyAllWindows()