#вариант для схемы проезд вдоль дуговой стены по правую руку 
import sys
import cv2
import imutils
import serial
import time
import math
from yoloDet import YoloTRT



# Ищем пару рядом стоящих доминошек слева и справа от вертикали (вертикальной линии в центре кадра).
# Ищем по средним нижним точкам BB (ограничивающих рамок). Как нашли присваивем значения:
# точка A (средняя точки нижней рамки левой доминошки) и точка B (средняя точка нижней рамки правой доминошки)


def poisk_ab(spisok_bb_x, spisok_bb_x_pravo, spisok_bb_y_pravo, spisok_bb_x_levo, spisok_bb_y_levo, vertikal):


    # Создаем список разностей между каждым элементом списка и vertikal,
    # заменяя 0 на 1, если разница равна 0
    raznosti = [(x - vertikal if x - vertikal != 0 else 1, x) for x in spisok_bb_x]


    # Разделяем разности на положительные и отрицательные
    polozhitelnye = [razn for razn in raznosti if razn[0] > 0]
    otricatelnye = [razn for razn in raznosti if razn[0] < 0]


    # Сортируем списки разностей по абсолютному значению разности
    polozhitelnye.sort(key=lambda x: abs(x[0]))
    otricatelnye.sort(key=lambda x: abs(x[0]))


    # Извлекаем минимальные положительную и отрицательную разности и их индексы
    min_polozhitelnaia_index = spisok_bb_x.index(polozhitelnye[0][1]) if polozhitelnye else None
    min_otricatelnaia_index = spisok_bb_x.index(otricatelnye[0][1]) if otricatelnye else None




    if min_otricatelnaia_index is not None:
        
        xa = spisok_bb_x[min_otricatelnaia_index]
        ya = spisok_bb_y_pravo[min_otricatelnaia_index]
    else:
        #print("Нет отрицательных разностей.")
        xa = None
        ya = None




    if min_polozhitelnaia_index is not None:
        xb = spisok_bb_x[min_polozhitelnaia_index]
        yb = spisok_bb_y_levo[min_polozhitelnaia_index]
    else:
        #print("Нет положительных разностей.")
        xb = None
        yb = None


    return xa, ya, xb, yb
# ------------------------------------------------------


def poisk_ab_seredina(spisok_bb_x, spisok_bb_x_levo, vertikal): # координаты середин доминошек, а затем левого угла для функции poisk()


    # Создаем список разностей между каждым элементом списка и vertikal,
    # заменяя 0 на 1, если разница равна 0
    raznosti = [(x - vertikal if x - vertikal != 0 else 1, x) for x in spisok_bb_x]


    # Разделяем разности на положительные и отрицательные
    polozhitelnye = [razn for razn in raznosti if razn[0] > 0]
    otricatelnye = [razn for razn in raznosti if razn[0] < 0]


    # Сортируем списки разностей по абсолютному значению разности
    polozhitelnye.sort(key=lambda x: abs(x[0]))
    otricatelnye.sort(key=lambda x: abs(x[0]))


    # Извлекаем минимальные положительную и отрицательную разности и их индексы
    min_polozhitelnaia_index = spisok_bb_x.index(polozhitelnye[0][1]) if polozhitelnye else None
    min_otricatelnaia_index = spisok_bb_x.index(otricatelnye[0][1]) if otricatelnye else None
   
    x_levo = spisok_bb_x_levo[min_otricatelnaia_index] # середина левой доминошки
 
    return x_levo
# ------------------------------------------------------





# Считаем угол альфа для определения горизонтальности AB

def ugol_alfa(xa, ya, xb, yb):
    hypotenuse_length = math.sqrt((xb - xa)**2 + (yb - ya)**2)
    alfa = math.atan2(abs(yb - ya), abs(xb - xa))
    #print("Альфа:",  int(alfa), "градусов")
    return math.degrees(alfa)
# ------------------------------------------------------


#команды прицеливания с поворотом на 1 

def pricelivanie(ac, cb, d_ac_cb, frame, arduino):
    popravka_na_pleho = AB/3
    print("pleho", popravka_na_pleho)
    
    if (ac+popravka_na_pleho)>cb and abs(ac+popravka_na_pleho-cb) > d_ac_cb:
        comand = "levo1|"        
        print("поворот на лево: levo1", int(ac+popravka_na_pleho-cb))
        cv2.putText(frame, "left!", (int(500), int(500)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)
        arduino.write(comand.encode())
        time.sleep(0.07)
    elif (ac+popravka_na_pleho)<cb and abs(ac+popravka_na_pleho-cb) > d_ac_cb:
        comand = "pravo1|"
        print("поворот на право: pravo1", int(ac+popravka_na_pleho-cb))
        cv2.putText(frame, "right!", (int(500), int(500)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)
        arduino.write(comand.encode())
        time.sleep(0.07)
    else:
        print()
        print("============ прицелились ===========", int(ac+popravka_na_pleho-cb))
        print()
        cv2.putText(frame, "ok", (int(500), int(500)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)
        global kluh_pricelilis
        kluh_pricelilis  = 1
        print("-----------------------Запуск функции pribligenie!---------------------------")
        print()
        


# ------------------------------------------------------


def pribligenie_start(ya, distanziy_start, frame, arduino):
    global kluh_start
    if distanziy_start > ya and kluh_start == 0:
        print("pribligenie_start", int(distanziy_start - ya))
        cv2.putText(frame, "go!", (int(500), int(500)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)
        comand = "pribligeniestart|" 
        arduino.write(comand.encode())
        time.sleep(0.1)
       
    else: # поворот на лево
        comand = "levostart|"  
        print("levostart")
        cv2.putText(frame, "left ~45", (int(500), int(500)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)
        arduino.write(comand.encode())
        time.sleep(1)
        kluh_start = 1
        


# ------------------------------------------------------


def pribligenie(ya, yb, distanziy, ac, cb, d_ac_cb, frame, arduino):

    global kluh_1BB
    global kluh_stop
    print("distanziy = ", distanziy)
    print("ya = ", ya)

    if distanziy > ya and kluh_start == 1:
         
        if yb is not None and kluh_1BB == 0:
            popravka_na_pleho = AB/3
                
            if (ac+popravka_na_pleho)>cb and abs(ac+popravka_na_pleho-cb) > d_ac_cb:
                comand = "levo1|"        
                print("prizel_end на лево: levo1", int(ac+popravka_na_pleho-cb))
                cv2.putText(frame, "left", (int(500), int(500)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)
                arduino.write(comand.encode())
                time.sleep(0.07)

            elif (ac+popravka_na_pleho)<cb and abs(ac+popravka_na_pleho-cb) > d_ac_cb:
                comand = "pravo1|"
                print("prizel_end на право: pravo1", int(ac+popravka_na_pleho-cb))
                cv2.putText(frame, "right", (int(500), int(500)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)
                arduino.write(comand.encode())
                time.sleep(0.07)

            else:
                print("************* pribligenie! *************", int(distanziy - ya))
                comand = "pribligenie|" 
                cv2.putText(frame, "go!!!", (int(500), int(500)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)
                arduino.write(comand.encode())
                time.sleep(0.3)
        else:
            print("************* pribligenie! (kluh_1BB = 1 ) *************", int(distanziy - ya))          

            comand = "pravoitog_" + str(ugol) + "|"  
            print()
            print("++++++++++++++++++ pravoitog (kluh_1BB = 1 ) +++++++++++++++++++", int(ac-cb))
            print()
            cv2.putText(frame, "right ~90 and GO!!!", (int(500), int(500)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)
            arduino.write(comand.encode())
            time.sleep(5)
            kluh_stop = 1
        
     
           
    else: # поворот на право
        comand = "pravoitog_" + str(ugol) + "|"  
        print()
        print("++++++++++++++++++ pravoitog +++++++++++++++++++", int(ac-cb))
        print()
        cv2.putText(frame, "right ~90 and GO!!!", (int(500), int(500)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)
        arduino.write(comand.encode())
        time.sleep(5)
        kluh_stop = 1
        
        

  
# ------------------------------------------------------

def ogibanie(kontrol_doezda, ef, kontrol, skorost, frame, arduino, xe, ye, xf, yf, vertikal, gorizontal_ef):

    if kontrol_doezda > 0:
        if ef<kontrol:
            comand = "levee_" + str(skorost) + "|"        
            print("движение левее: levee", ef-kontrol, skorost, comand)            
            cv2.putText(frame, "to the left", (int(500), int(500)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)
            arduino.write(comand.encode())
            time.sleep(0.09)
        else:
            comand = "pravee|"
            print("движение правее: pravee", ef-kontrol)            
            cv2.putText(frame, "to the right", (int(500), int(500)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)
            arduino.write(comand.encode())
            time.sleep(0.07)
        # Отрисовка линии EF
        cv2.line(frame, (int(xe), int(ye)), (int(xf), int(yf)), (0, 255, 0), 4)
        # Отрисовка текста значения xf на линии
        cv2.putText(frame, str(int(ef)), (int(vertikal+20), int(gorizontal_ef-20)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
        
    else: 
        comand = "pryamo|"
        print("движение pryamo: pryamo", kontrol_doezda)        
        cv2.putText(frame, "go", (int(500), int(500)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)
        arduino.write(comand.encode())
        time.sleep(0.11)
        # Отрисовка стрелки вверх
        cv2.line(frame, (int(xe), int(ye)), (int(xe), int(ye-abs(kontrol_doezda))), (0, 255, 0), 4)
        
    

# ------------------------------------------------------
# ------------------------------------------------------


try:
    arduino = serial.Serial(
        port='/dev/ttyUSB0',  # Укажите правильный порт, к которому подключен Arduino
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1
    )


    # Загружаем YOLOv5 в формате TensorRT с плагинами, готовую к предсказаниям при conf=0.6
    model = YoloTRT(library="yolov5/build/libmyplugins.so", engine="yolov5/build/best_domino_pol_050524.engine", conf=0.6, yolo_ver="v5")

    # Параметры для доступа к камере через GStreamer
    gst_str = (
    "nvarguscamerasrc ! "
    "video/x-raw(memory:NVMM), width=720, height=540, framerate=30/1, format=NV12 ! "
    "nvvidconv flip-method=0 ! "
    "video/x-raw, width=720, height=540, format=BGRx ! "
    "videoconvert ! "
    "video/x-raw, format=BGR ! appsink"
     )


# Открытие потока камеры с использованием GStreamer
    cap = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)

 

    if not cap.isOpened():
        print("Error: Could not open video device.")
        exit()
   
    frame_count = 0
    global ugol
    global AB
    kluh_start = 0  # для доезда до точки поворота после старта, после которой происходит огибание стены в поисках выхода
    kluh_pricelilis = 0  # для доезда до точки поворота, после которой происходит выезд из лабиринта
    kluh_1BB = 0 # для выезда по одному BB (ограничивающей рамки)
    kluh_stop = 0 #stop
    AB = 0
    

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        frame_count += 1
        if frame_count % 15 != 0:  # Обрабатываем только каждый 15-й кадр для снижения нагрузки на Jetson
            continue

        frame = imutils.resize(frame, width=720)
        detections, t = model.Inference(frame)

        spisok_bb_y_levo = []  # y левого угла рамок
        spisok_bb_y_pravo = []  # y правого угла рамок
        spisok_bb_x_levo = []  # x левого угла рамок
        spisok_bb_x_pravo = []  # x правого угла рамок

        for obj in detections:
            boxxx = obj['box']
            spisok_bb_y_levo.append(boxxx[3]) # y левого угла рамок
            spisok_bb_y_pravo.append(boxxx[3]) # y правого угла рамок
            spisok_bb_x_levo.append(boxxx[0])  # x левого угла рамок
            spisok_bb_x_pravo.append(boxxx[2])  # x правого угла рамок


        ugol = 20  # пороговый угол горизонтальности 
        
        gorizontal_ef = 230 
        kontrol = 0
        vertikal = 360 # значение x-координаты цента кадра
        d_ac_cb = 30  # порог разницы AC и CB  
        skorost = 700
        distanziy = 300
        distanziy_start = 250
        AB_END = 300 # при AB больше 300 считаем, что нашли выход

         # Отрисовка линии gorizontal_ef
        cv2.line(frame, (vertikal-20, int(gorizontal_ef)), (vertikal+20, int(gorizontal_ef)), (255, 0, 0), 1)

        # Отрисовать вертикальную линию
        cv2.line(frame, (vertikal, gorizontal_ef), (vertikal, gorizontal_ef-20), (255, 0, 0), 2)




        # Создаем список нижних средних точек на основе значений из spisok_bb_x_levo и spisok_bb_x_pravo
        spisok_bb_x = [(spisok_bb_x_levo[i] + (spisok_bb_x_pravo[i] - spisok_bb_x_levo[i]) / 2) for i in range(len(spisok_bb_x_levo))]

        # Среди всех ББ ищем левую и правую доминошки относительно горизонтали и их координты точек: 
        # точка A (правая нижняя средняя точка ББ левой доминошк и точка B (левая нижняя средняя точка правой доминошки)
        xa, ya, xb, yb = poisk_ab(spisok_bb_x, spisok_bb_x_pravo, spisok_bb_y_pravo, spisok_bb_x_levo, spisok_bb_y_levo, vertikal) 
        
        if None in (xa, ya, xb, yb):     	
            print('no 2BB')     
        

        else:
            
            ac = abs(vertikal - xa)
            cb = abs(xb - vertikal)
            
            alfa = ugol_alfa(xa, ya, xb, yb) # угол между AB и горизонталью        
            
            b1b = abs(xb - vertikal)
            eb1 = abs(yb - gorizontal_ef)
            aa1 = abs(vertikal - xa)
            a1b1 = abs(yb - ya)

            ef = b1b - (eb1 * (aa1 + b1b) / a1b1)

            AD = yb - ya
            DB = xb - xa
            AB = (AD * AD + DB * DB) ** 0.5 # длина AB

            kontrol_doezda = yb-gorizontal_ef

            if ef > -1000 and ef < -100:
                skorost = 1000            
            elif ef >= -100 and ef < -50:
                skorost = 950
            elif ef >= -50 and ef < 0:
                skorost = 900
            else: 
                skorost = 800
 
            xe = vertikal
            ye = gorizontal_ef
            xf = vertikal + ef
            yf = gorizontal_ef

            print('ef =', int(ef), int(skorost))
            print('yb =', int(yb), int(kontrol_doezda))
            print('ya =', int(ya))
            print('AB =', int(AB))       

            # Отрисовать линию AB
            cv2.line(frame, (int(xa), int(ya)), (int(xb), int(yb)), (0, 0, 255), 2)  # Красная линия толщиной 2 пикселя


        print('kluh_pricelilis = ', kluh_pricelilis)
        print('kluh_start = ', kluh_start)
        print('kluh_1BB = ', kluh_1BB)




        if kluh_start == 0:
            pribligenie_start(ya, distanziy_start, frame, arduino)
 
        elif kluh_stop == 1:
            time.sleep(5)
            exit()

        elif kluh_pricelilis == 1:
            pribligenie(ya, yb, distanziy, ac, cb, d_ac_cb, frame, arduino)

        else:           
           
            if AB > AB_END: # нашли выход
                print('pricelivanie')
                pricelivanie(ac, cb, d_ac_cb, frame, arduino)
            else:
                print('ogibanie') # продолжаем движение (огибание) вдоль стены из домино
                ogibanie(kontrol_doezda, ef, kontrol, skorost, frame, arduino, xe, ye, xf, yf, vertikal, gorizontal_ef)
  
      

        

        cv2.imshow("Output", frame)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break

        time.sleep(0.01)  # Добавить небольшую задержку, чтобы снизить нагрузку на процессор

finally:
    # Закрытие соединения с Arduino
    if 'arduino' in locals():    
        arduino.close()

    # Освобождение захватчика видео и закрытие окон OpenCV
    cap.release()    
    cv2.destroyAllWindows()
