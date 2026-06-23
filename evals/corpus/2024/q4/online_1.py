import re
import numpy as np

def read_input_file(input_file):
  try:
      with open(input_file,'r') as f:
        matrix =np.array([list(l.strip()) for l in f])
  except FileNotFoundError:
    print(f"Error: The input file '{input_file}' was not found.")
    exit(1)
  return matrix


def part1(matrix):
 # using lookahead to get count also overlapping matchings
  pattern = re.compile(r'(?=XMAS|SAMX)')
  # counts the number of matches in string
  pattern_count = lambda string: pattern.subn(r'',string)[1]

  m,n = matrix.shape
  num = 0
  # count matches in:
  # ..rows
  num += sum(pattern_count(''.join(r)) for r in matrix)
  # ..columns
  num += sum(pattern_count(''.join(matrix[:,j])) for j in range(n))
  # ..main diagonals (from top-left to bottom-right)
  num += sum(pattern_count(''.join(matrix.diagonal(d))) for d in range(-m+4,n-3))
  # ..anti-diagonals (from top-right to bottom-left)
  num += sum(pattern_count(''.join(np.fliplr(matrix).diagonal(d))) for d in range(-m+4,n-3))

  print("Solution for part 1:",num)

def part2(matrix):
  m,n = matrix.shape
  isSM = lambda mat: {mat[0,0], mat[2,2]} == {'S','M'} and {mat[0,2], mat[2,0]} == {'S','M'}

  res = sum(1 for i in range(1,m-1) for j in range(1,n-1) if matrix[i,j]=='A' and isSM(matrix[i-1:i+2,j-1:j+2]))
  print("Solution for part 2: ", res)

def main():
  input_file = "input4.txt"
  matrix = read_input_file(input_file)
  part1(matrix)
  part2(matrix)

if __name__ == '__main__':
  main()
