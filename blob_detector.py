import cv2
import numpy as np

def detect_blobs(input_image, staffs):
    """
    поиск блобов по заданным параметрам.
    """
    print("поиск нот")
    im_with_blobs = input_image.copy()

    im_inv = (255 - im_with_blobs)#инвертируем изображение
    #ядро для морф.трансформации, является квадратом с высотой = 1,шириной=шириналиста/250
    kernel = cv2.getStructuringElement(ksize=(1, int(im_inv.shape[0] / 500)), shape=cv2.MORPH_RECT)#для фото
    #kernel = cv2.getStructuringElement(ksize=(1, int(im_inv.shape[0] / 300)), shape=cv2.MORPH_RECT)
    horizontal_lines = cv2.morphologyEx(im_inv, cv2.MORPH_OPEN, kernel)
    #убираем горизонтальные линии просто меняя их цвет 
    horizontal_lines = (255 - horizontal_lines)

    #kernel = cv2.getStructuringElement(ksize=(int(im_inv.shape[1] / 250), 1), shape=cv2.MORPH_RECT)#для фото
    kernel = cv2.getStructuringElement(ksize=(int(im_inv.shape[1] / 200), 1), shape=cv2.MORPH_RECT)
    vertical_lines = cv2.morphologyEx(255 - horizontal_lines, cv2.MORPH_OPEN, kernel)
    vertical_lines = (255 - vertical_lines)

    cv2.imwrite("output/8a_lines_horizontal_removed.png", horizontal_lines)
    cv2.imwrite("output/8a_lines_vertical_removed.png", vertical_lines)

    im_with_blobs = vertical_lines
    im_with_blobs = cv2.cvtColor(im_with_blobs, cv2.COLOR_GRAY2BGR)

    #настраиваем параметры blob-ов для поиска на изображении
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True#фильтрация по площади
    params.minArea = 225#минимальная площадь в пикселях
    params.maxArea = 1500#максимальная площадь
    params.filterByCircularity = True#фильтрация по круглости, тк нота круглая
    params.minCircularity = 0.6#минимальная круглость
    params.filterByConvexity = True#фильтрация по выпуклости
    params.minConvexity = 0.9#минимальная выпуклость
    params.filterByInertia = True
    params.minInertiaRatio = 0.01

    detector = cv2.SimpleBlobDetector_create(params)#создание детектора с существующими параметрами
    keypoints = detector.detect(im_with_blobs)#нахождение нот с помощью детектора
    for keypoint in keypoints:
        print(int(keypoint.pt[0]))
    cv2.drawKeypoints(im_with_blobs, keypoints=keypoints, outImage=im_with_blobs, color=(0, 0, 255),
                     flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)#отрисовка блобов на изображении
    cv2.imwrite("output/8b_with_blobs.jpg", im_with_blobs)

    '''
    нумерация нот
    '''
    staff_diff = 3 / 5 * (staffs[0].max_range - staffs[0].min_range)#разница между максимальным и минимальным значением стана * 3/5
    bins = [x for sublist in [[staff.min_range - staff_diff, staff.max_range + staff_diff] for staff in staffs] for x in
            sublist]#список, содержащий диапазоны координат y для каждого нотного стана по y
    keypoints_staff = np.digitize([key.pt[1] for key in keypoints], bins)#индекс каждого блоба на основе его координаты
    #np.digitize - используется для нахождения индекса ближайшего значения в заданном массиве для каждого элемента входного массива.
    sorted_notes = sorted(list(zip(keypoints, keypoints_staff)), key = lambda tup: (tup[1], tup[0].pt[0]))

    im_with_numbers = im_with_blobs.copy()
    for idx, tup in enumerate(sorted_notes):
        cv2.putText(im_with_numbers, str(idx), (int(tup[0].pt[0]), int(tup[0].pt[1])),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=4, color=(255, 0, 0))
        cv2.putText(im_with_blobs, str(tup[1]), (int(tup[0].pt[0]), int(tup[0].pt[1])),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=4, color=(255, 0, 0))
    cv2.imwrite("output/8c_with_numbers.jpg", im_with_numbers)
    cv2.imwrite("output/8d_with_staff_numbers.jpg", im_with_blobs)

    print("всего найденно элементов : " + str(len(keypoints)))

    return sorted_notes
