from midiutil import MIDIFile

def mk_track(notes):
# Создание MIDI-файла
    midi = MIDIFile(1)  # Создание нового MIDI-файла с одним треком
    track = 0  # Номер трека
    channel = 0  # Номер канала
    time = 1  # Время начала ноты
    duration = 3  # Длительность ноты
    tempo = 100  # Темп в ударах в минуту
    volume = 100
    # Установка темпа
    midi.addTempo(track, time, tempo)
    # Пример названий нот
    notes_midi = {#словарь, содержащий соотв нота-позиция
        'E6':88,
        'D6':86,
        'C6':84,
        'H5':83,
        'A5':81,
        'G5':79,
        'F5':77,
        'E5':76,
        'D5':74,
        'C5':72,
        'H4':71,
        'A4':69,
        'G4':67,
        'F4':65,
        'E4':64,
        'D4':62,
        'C4':60,
        'H3':59,
        'A3':57,
        'G3':55,
        'F3':53,
    }
    
    l_of_midi = []
    for i in notes:
        if i in notes_midi:
            l_of_midi.append(notes_midi[i])
    # Передача нот и их высоты в MIDI-файл
    for i in l_of_midi:
        midi.addNote(track, channel, i, time, duration,volume)
        time += 1
        # Сохранение MIDI-файла
    with open('output.mid', 'wb') as file:
        midi.writeFile(file)
