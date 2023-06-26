class Staff:
    """
    для поиска нотных станов
    """
    def __init__(self, min_range, max_range):
        self.min_range = min_range
        self.max_range = max_range
        self.lines_location, self.lines_distance = self.get_lines_locations()

    def get_lines_locations(self):
        """
        вычисление приблизительных позиций строк на пятилинейном стане

        :return: список примерных положений строк.
        """
        lines = []
        lines_distance = int((self.max_range - self.min_range) / 4)
        for i in range(5):
            lines.append(self.min_range + i * lines_distance)
        return lines, lines_distance