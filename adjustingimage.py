from config import distance
import cv2
import numpy as np
import sys

def check(image):
    img = image.copy()
    # Конвертация в оттенки серого
    im_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Применение пороговой бинаризации
    ret, threshold = cv2.threshold(im_gray, 100, 255, cv2.THRESH_BINARY)
    # Нахождение контуров на бинаризованном изображении
    contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # Рассчитываем площадь изображения и площадь наибольшего контура
    image_area = img.shape[0] * img.shape[1]
    largest_contour_area = max([cv2.contourArea(cnt) for cnt in contours])
    # Если площадь наибольшего контура меньше 90% площади изображения, значит на изображении есть фон
    if largest_contour_area < 0.9 * image_area:
        print("Изображение содержит фон")
        result = adjust_image(image)
    else:
        print("На изображении только объекты без фона")
        result = adjust_scan(image)
    
    return result
    
def adjust_image(image):
    #преобразования изображения rgb в оттенки серого
    gray = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)#0.114 * blue_pixel + 0.299 * red_pixel + 0.587 * green_pixel 
    cv2.imwrite("output/gray.jpg", gray)#сохранение изображения в оттенках серого
    
    blur = cv2.GaussianBlur(gray, (7,7), 0)#размытие с помощью фильтра гаусса
    cv2.imwrite('output/blur.jpg',blur)#сохранение размытого изображения
    
    edged = cv2.Canny(blur, 0, 50)#обнаружение краев, представление изображения массивом ч/б пикселей
    cv2.imwrite('output/canny.jpg', edged)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)
    
    cv2.imwrite('output/closed.jpg', closed)
    contours, _ = cv2.findContours(closed, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE) # поиск контуров
    
    
    contours = sorted(contours, key=cv2.contourArea, reverse=True)#сортировка по площади контура

    for cnt in contours:
    # Douglas Pecker algorithm -  для упрощения контуров изображений
    # поиск на изображении контура, который имеет четыре угл
        epsilon = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.01 * epsilon, True)
        if len(approx) == 4:
            sheet = approx
            break

    if 'sheet' not in locals():
        print("невозможно найти лист на фото")
        sys.exit()

    approx = np.asarray([x[0] for x in sheet.astype(dtype=np.float32)])#массив из 4х углов изображения
    
    # top_left has the smallest sum, bottom_right has the biggest
    top_left = min(approx, key=lambda t: t[0] + t[1])
    bottom_right = max(approx, key=lambda t: t[0] + t[1])
    top_right = max(approx, key=lambda t: t[0] - t[1])
    bottom_left = min(approx, key=lambda t: t[0] - t[1])
    
    max_width = int(max(distance(bottom_right, bottom_left), distance(top_right, top_left)))#максимальная ширина изображения
    max_height = int(max(distance(top_right, bottom_right), distance(top_left, bottom_left)))#максимальная высота изображения
    
    arr = np.array([#массив, состоящий из координат исходного изображения, 4 координаты которого - вершины прямоугольника
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1]], dtype="float32")
    
    rectangle = np.asarray([top_left, top_right, bottom_right, bottom_left])#координаты прямоугольника(листа)
    #преобразование перспективы, фотография становится сканом листа
    m = cv2.getPerspectiveTransform(rectangle, arr)
    dst = cv2.warpPerspective(image, m, (max_width, max_height))
    
    cv2.drawContours(image, contours, -1, (0, 255, 0), 2)
    cv2.imwrite("output/2with_contours.png", image)
    dst = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)

    _, result = cv2.threshold(dst, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    cv2.imwrite("output/3adjusted_photo.png", result)
    return result

def adjust_scan(image):
    gray = cv2.cvtColor(image.copy(), cv2.COLOR_RGB2GRAY)
    _, result = cv2.threshold(gray, 200,255, cv2.THRESH_BINARY)
    cv2.imshow('Image', result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    h,w = result.shape[:2]
    new_h = h * 3
    new_w = w * 3
    resized_img = cv2.resize(result, (new_w, new_h)) # изменение размера
    cv2.imwrite('output/3resized.png', resized_img)
    return resized_img