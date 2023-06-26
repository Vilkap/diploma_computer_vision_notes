import cv2

from config import distance
NOTE_PITCH_DETECTION_MIDDLE_SNAPPING = 6
violin_key = {#словарь, содержащий соотв позиция-нота
    -6: 'E6',
    -5: 'D6',
    -4: 'C6',
    -3: 'H5',
    -2: 'A5',
    -1: 'G5',
    0:  'F5',
    1:  'E5',
    2:  'D5',
    3:  'C5',
    4:  'H4',
    5:  'A4',
    6:  'G4',
    7:  'F4',
    8:  'E4',
    9:  'D4',
    10: 'C4',
    11: 'H3',
    12: 'A3',
    13: 'G3',
    14: 'F3',
}

def extract_notes(blobs, staffs):
    #принимает блобы, информацию о нотных станах и изображение
    #возвращает список всех нот
    notes = []
    print('Обнаружение нот из блобов.')
    for blob in blobs:
        if blob[1] % 2 == 1:
            staff_no = int((blob[1] - 1) / 2)
            notes.append(Note(staff_no, staffs, blob[0], violin_key))
    print('Обнаружено ' + str(len(notes)) + ' нот.')
    return notes


def draw_notes_pitch(image, notes):
    im_with_pitch = image.copy()
    im_with_pitch = cv2.cvtColor(im_with_pitch, cv2.COLOR_GRAY2BGR)
    for note in notes:
        cv2.putText(im_with_pitch, note.pitch, (int(note.center[0]) - 20, int(note.center[1]) + 50),#размещение названия нот
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=2, color=(0, 0, 0))
    cv2.imwrite('output/9_with_pitch.png', im_with_pitch)

#для того, чтобы воспроизвести ноты, сначала их нужно добавить в массив
def notes_to_midi(notes):
    list_of_notes = []
    for i in notes:
        list_of_notes.append(i.detect_pitch(i.position_on_staff))
    return list_of_notes


class Note:
    """
    Конструктор принимает номер нотного стана,
    список всех нотных станов, блоб с нотным символом и ключ
    """
    def __init__(self, staff_no, staffs, blob, clef):
        self.position_on_staff = self.detect_position_on_staff(staffs[staff_no], blob)#позиция ноты на стане
        self.staff_no = staff_no#номер нотного стана
        self.center = blob.pt#центр нотного стана
        self.pitch = self.detect_pitch(self.position_on_staff)#высота ноты относительно позиции
    #функция определения позиции ноты на нотном стане
    def detect_position_on_staff(self, staff, blob):
        distances_from_lines = []#список, содержащий в себе расстояния от координаты x,y блоба до каждой линиии на нотном стане
        x, y = blob.pt#координаты x,y каждого блоба
        for line_no, line in enumerate(staff.lines_location):
            distances_from_lines.append((2 * line_no, distance((x, y), (x, line))))
        # генерация 3х дополнительных линий сверху
        for line_no in range(5, 8):
            distances_from_lines.append((2 * line_no, distance((x, y), (x, staff.min_range + line_no * staff.lines_distance))))
        # генерация 3х доп линиий снизу
        for line_no in range(-3, 0):
            distances_from_lines.append((2 * line_no, distance((x, y), (x, staff.min_range + line_no * staff.lines_distance))))

        distances_from_lines = sorted(distances_from_lines, key=lambda tup: tup[1])
        # Проверьте, находится ли разница между двумя ближайшими расстояниями в пределах 6
        if distances_from_lines[1][1] - distances_from_lines[0][1] <= NOTE_PITCH_DETECTION_MIDDLE_SNAPPING:
            # размещение ноты между 2мя линиями
            return int((distances_from_lines[0][0] + distances_from_lines[1][0]) / 2)
        else:
            # размещение ноты, являющейся ближайшей к центру блоба
            return distances_from_lines[0][0]

    def detect_pitch(self, position_on_staff):
        return violin_key[position_on_staff]
