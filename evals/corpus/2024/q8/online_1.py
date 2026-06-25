class Solution:

    def __init__(self, filename):

        self.antenas_freq_dict, self.antenas_map, self.max_map_bound = self.read_input(filename=filename) # Stores antenas in dictionary on the basis of frequency (key of dict)

        self.puzzle_number = -1

    def read_input(self,filename):

        antenas_freq_dict = {}

        max_map_bound = 0

        antenas_map = []

        try:

            with open(filename, 'r') as f:

                row_index = 0

                raw_data_lines = f.read().split('\n')

                max_map_bound = len(raw_data_lines)

                for line in raw_data_lines:

                    line = list(line)

                    antenas_map.append(line)

                    col_index = 0

                    for col in line:

                        if col != '.':

                            cords = (row_index,col_index)

                            if col in antenas_freq_dict:
                                antenas_freq_dict[col].append(cords)
                            else:
                                antenas_freq_dict[col] = [cords]

                        col_index += 1

                    row_index += 1

        except Exception as e:

            print("Error in read_input():", e)

        return antenas_freq_dict, antenas_map, max_map_bound

    def resonate_antinodes(self, antena, row_offset, col_offset):

        """
        (Resonance) Generate antinodes for antena aligned to other same frequency antena.
        """

        resonated_antinodes = set()

        resonated_antinodes.add(antena)

        prev_antinode = antena

        while True:

            new_antinode = (prev_antinode[0]+row_offset, prev_antinode[1]+col_offset)

            if new_antinode[0] >= 0 and new_antinode[0] < self.max_map_bound and new_antinode[1] >=0 and new_antinode[1] < self.max_map_bound:

                self.antenas_map[new_antinode[0]][new_antinode[1]] = '#'

                resonated_antinodes.add(new_antinode)

                prev_antinode = new_antinode

            else:

                break

        return resonated_antinodes

    def create_antinodes(self):

        """
        An antinode occurs at any point that is perfectly in line with two antennas of the same frequency
        - but only when one of the antennas is twice as far away as the other.
        This means that for any pair of antennas with the same frequency, there are two antinodes, one on either side of them.
        """

        antinodes = set()

        for freq  in self.antenas_freq_dict:

            freq_antenas = self.antenas_freq_dict[freq]

            freq_antenas_length = len(freq_antenas)

            for i in range(freq_antenas_length):

                antena_1 = freq_antenas[i]

                for j in range(i+1,freq_antenas_length):

                    antena_2 = freq_antenas[j]

                    row_diff = abs(antena_1[0]-antena_2[0])

                    col_diff = abs(antena_1[1]-antena_2[1])

                    new_antinodes = []

                    if antena_1[1] < antena_2[1]:

                        if antena_1[0] > antena_2[0]:

                            if self.puzzle_number == 1:

                                new_antinodes.append((antena_1[0]+row_diff, antena_1[1]-col_diff)) # left antinode

                                new_antinodes.append((antena_2[0]-row_diff, antena_2[1]+col_diff)) # right antinode

                            elif self.puzzle_number == 2:

                                antinodes = antinodes.union(self.resonate_antinodes(antena_1, row_diff, -col_diff)) # Resonate left antinode

                                antinodes = antinodes.union(self.resonate_antinodes(antena_2, -row_diff, col_diff)) # Resonate right antinode

                        else:

                            if self.puzzle_number == 1:

                                new_antinodes.append((antena_1[0]-row_diff, antena_1[1]-col_diff)) # left antinode

                                new_antinodes.append((antena_2[0]+row_diff, antena_2[1]+col_diff)) # right antinode

                            elif self.puzzle_number == 2:

                                antinodes = antinodes.union(self.resonate_antinodes(antena_1, -row_diff, -col_diff)) # Resonate left antinode

                                antinodes = antinodes.union(self.resonate_antinodes(antena_2, row_diff, col_diff)) # Resonate right antinode

                    else:

                        if antena_2[0] > antena_1[0]:

                            if self.puzzle_number == 1:

                                new_antinodes.append((antena_2[0]+row_diff, antena_2[1]-col_diff)) # left antinode

                                new_antinodes.append((antena_1[0]-row_diff, antena_1[1]+col_diff)) # right antinode

                            elif self.puzzle_number == 2:

                                antinodes = antinodes.union(self.resonate_antinodes(antena_2, row_diff, -col_diff)) # Resonate left antinode

                                antinodes = antinodes.union(self.resonate_antinodes(antena_1, -row_diff, col_diff)) # Resonate right antinode


                        else:

                            if self.puzzle_number == 1:

                                new_antinodes.append((antena_2[0]-row_diff, antena_2[1]-col_diff)) # left antinode

                                new_antinodes.append((antena_1[0]+row_diff, antena_1[1]+col_diff)) # right antinode

                            elif self.puzzle_number == 2:

                                antinodes = antinodes.union(self.resonate_antinodes(antena_2, -row_diff, -col_diff)) # Resonate left antinode

                                antinodes = antinodes.union(self.resonate_antinodes(antena_1, row_diff, col_diff)) # Resonate right antinode


                    # Add only map bound antinodes

                    if self.puzzle_number == 1:

                        for anti in new_antinodes:

                            if anti[0] >= 0 and anti[0] < self.max_map_bound and anti[1] >=0 and anti[1] < self.max_map_bound:

                                self.antenas_map[anti[0]][anti[1]] = '#'

                                antinodes.add(anti)

        return antinodes

    def show_map(self):

        for row in self.antenas_map:

            print("".join(row))

    def solve(self, puzzle_number):

        self.puzzle_number = puzzle_number

        antinodes = self.create_antinodes()

        return len(antinodes)

if __name__ == "__main__":

    s = Solution('input-day-8.txt')

    answer_puzzle_1 = s.solve(puzzle_number=1)

    print("Answer of Puzzle#1:", answer_puzzle_1)

    answer_puzzle_2 = s.solve(puzzle_number=2)

    print("Answer of Puzzle#2:", answer_puzzle_2)
