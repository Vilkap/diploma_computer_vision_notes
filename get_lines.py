import cv2
import numpy as np

from staff import Staff
import sys

def get_staffs(image):
    """
    Данная функция возвращает список нотных станов
    на входе - изображение,для которого нужно найти нотные станы
    на выходе - список найденных нотных станов
    """
    processed_image, thresholded = preprocess_image(image)
    all_lines, lines_image_color = detect_lines(processed_image,thresholded, 80)
    staffs = detect_staffs(all_lines)
    draw_staffs(lines_image_color, staffs)
    return [Staff(staff[0], staff[1]) for staff in staffs]

def preprocess_image(image):
    #Приготовление изображения для последующего преобразования
    print("Предварительная обработка изображения.")
    gray = image.copy()
    _, thresholded = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY)#всё,что выше - белый, ниже - черный
    element = np.ones((3, 3))#ядро эррозии
    #применение эрозии для изображения. если все пиксели в ядре равны 1, то пиксель будет 1, 
    #если же хотя бы 1 не будет равен 1, то текущий пиксель - 0
    thresholded = cv2.erode(thresholded, element)
    edges = cv2.Canny(thresholded, 10, 100, apertureSize=3)
    cv2.imwrite('output/5.1edges.png', edges)
    return edges, thresholded

def detect_lines(processed_image,image, nlines):
    """
    Данная функция используется для обнаружения горизонтальных линий
    на изображении и добавляет их в список.
    """
    print("Распознавание линий.")
    #ищем линии по заданным параметрам
    #преобразование Хафа для поиска линий на изображении
    hough = cv2.HoughLines(processed_image, 1, np.pi / 150, 200)
    all_lines = set()#множество линий
    width, height = image.shape#получаем высоту и ширину изображения
    #делаем изображение цветным, чтобы можно было увидеть найденные линии.
    lines_image_color = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    for result_arr in hough[:nlines]:
        #линия представлена в параметрическом виде: 
        #r = x*cos(theta) + y*sin(theta), 
        #где r - длина перпендикуляра от начала координа до линии
        #а theta - угол между r и x
        rho = result_arr[0][0]
        #print(rho)
        theta = result_arr[0][1]
        a = np.cos(theta)
        b = np.sin(theta)

        x0 = a * rho
        y0 = b * rho
        shape_sum = width + height
        #координаты линий
        x1 = int(x0 + shape_sum * (-b))
        y1 = int(y0 + shape_sum * a)
        x2 = int(x0 - shape_sum * (-b))
        y2 = int(y0 - shape_sum * a)

        start = (x1, y1)#начальная координата линии
        end = (x2, y2)#конечная координата
        diff = y2 - y1#разность по вертикали
        if abs(diff) < 10:#если разность меньше 10, то добавляем
            all_lines.add(int((start[1] + end[1]) / 2))#средняя координата по y
            cv2.line(lines_image_color, start, end, (0, 0, 255), 2)#отрисовка найденной линии
    
    if len(all_lines) < 5:
        print('На изображении нет достаточного количества линий для нотного стана')
        sys.exit()
        
    cv2.imwrite("output/5lines.png", lines_image_color)
    
    return all_lines, lines_image_color


def detect_staffs(all_lines):
    """
    Нахождение нотных станов на изображении
    возвращает начало и конец обнаруженного нотного стана
    """
    print("Поиск нотных станов")
    LINES_DISTANCE_THRESHOLD = 50
    staffs = []#список, в котором хранится начало и конец нотного стана
    lines = []#список координат линий текущего стана
    all_lines = sorted(all_lines)#сортируем линии по возрастанию
    for current_line in all_lines:
        # если список не пустой и расстояние между текущей лtинией и последней
        #обнаруженной линией больше порога Lines_distant
        if lines and abs(lines[-1] - current_line) > 50:
            if len(lines) >= 5:
                # Если больше 5, то начало это начало нового стана
                # если меньше 5, то не нотный стан
                staffs.append((lines[0], lines[-1]))#добавляем в список нотных станов 1ю и 5ю линию
            lines.clear()
        lines.append(current_line)

    # Process the last line
    if len(lines) >= 5:#если больше 5, то нотный стан
    #расстояние между предпоследней и последней меньше 50
        if abs(lines[-2] - lines[-1]) <= LINES_DISTANCE_THRESHOLD:
            staffs.append((lines[0], lines[-1]))
    return staffs


def draw_staffs(image, staffs):
    """
    отрисовка станов на нотном листе
    """
    # Draw the staffs
    width = image.shape[0]
    for staff in staffs:
        cv2.line(image, (0, staff[0]), (width, staff[0]), (0, 255, 0), 4)
        cv2.line(image, (0, staff[1]), (width, staff[1]), (0, 255, 0), 4)
    cv2.imwrite("output/6staffs.png", image)
