import cv2
from adjustingimage import check
from get_lines import get_staffs
import os.path as pth
from blob_detector import detect_blobs
from note import extract_notes, draw_notes_pitch,notes_to_midi
#from notes_to_midi import mk_track
file_path = 'input/18.jpg'
    
def main():
    if not pth.exists(file_path):#проверка существования файла
        return 'Исходный файл не существует'
    else: image = cv2.imread(file_path)#читаем изображение
    processed_photo = check(image)#подготовка изображения для дальнейшей работы
    staffs = get_staffs(processed_photo)#нахождение и отрисовка нотных станов на изображении
    blobs = detect_blobs(processed_photo, staffs)#поиск блобов на изображении по заданным параметрам
    notes = extract_notes(blobs, staffs)#поиск и классификация нот на нотных станах
    draw_notes_pitch(processed_photo, notes)#отрисовка нот
    nlist = notes_to_midi(notes)#получение списка нот, обнаруженных на изображении
    #mk_track(nlist)
    print(nlist)
if __name__ == '__main__':
    main()

'''
 im = Image.open('output/3adjusted_photo.png')
 length,width = im.size#длина ширина
 for i in range(length):
     for j in range(width):
         if im.getpixel((i,j)) == 255:
             im.putpixel((i,j),(255,255))
 im.show()
 cv2.imshow("output/3adjusted_photo.png", processed_photo)
 cv2.waitKey(0)
 cv2.destroyAllWindows()
'''