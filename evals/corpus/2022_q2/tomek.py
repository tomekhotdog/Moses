from typing import List
from main import read_input
from enum import Enum


SCORE_WIN = 6
SCORE_DRAW = 3
SCORE_LOSE = 0


class Play(Enum):
    ROCK = 1
    PAPER = 2
    SCISSORS = 3


# How to decypher X/Y/Z -> ROCK/PAPER/SCISSORS.
class DecypherStrategy(Enum):
    # Strategy used in part 1 - X/Y/Z maps to a specific play.
    PRESCRIBED_PLAY = 1
    # Strategy used in part 2: X/Y/Z maps to a specific result that should be achieved.
    PRESCRIBED_RESULT = 2


class Round:
    def __init__(self, opponent_play: Play, my_play: Play):
        self.opponent_play = opponent_play
        self.my_play = my_play

    def __str__(self):
        return f"{self.opponent_play} vs {self.my_play}"


def parse_opponent_play(play: str) -> Play:
    match play:
        case 'A':
            return Play.ROCK
        case 'B':
            return Play.PAPER
        case 'C':
            return Play.SCISSORS
        case _:
            raise Exception("Unknown play: " + str(play))


def parse_my_play(strategy: DecypherStrategy, opponent_play_str: str, my_play_str: str) -> Play:
    if strategy == DecypherStrategy.PRESCRIBED_PLAY:
        match my_play_str:
            case 'X':
                return Play.ROCK
            case 'Y':
                return Play.PAPER
            case 'Z':
                return Play.SCISSORS
            case _:
                raise Exception("Unknown play: " + str(my_play_str))
    if strategy == DecypherStrategy.PRESCRIBED_RESULT:
        opponent_play = parse_opponent_play(opponent_play_str)
        match opponent_play, my_play_str:
            case Play.ROCK, 'X':
                return Play.SCISSORS
            case Play.ROCK, 'Y':
                return Play.ROCK
            case Play.ROCK, 'Z':
                return Play.PAPER
            case Play.PAPER, 'X':
                return Play.ROCK
            case Play.PAPER, 'Y':
                return Play.PAPER
            case Play.PAPER, 'Z':
                return Play.SCISSORS
            case Play.SCISSORS, 'X':
                return Play.PAPER
            case Play.SCISSORS, 'Y':
                return Play.SCISSORS
            case Play.SCISSORS, 'Z':
                return Play.ROCK
            case _:
                raise Exception("Failed to parse: " + str(opponent_play) + " " + my_play_str)


def parse_round(strategy: DecypherStrategy, game_round: str) -> Round:
    plays = game_round.split(' ')
    opponent_play = parse_opponent_play(plays[0])
    my_play = parse_my_play(strategy, plays[0], plays[1])
    return Round(opponent_play, my_play)


def score_play(game_round: Round) -> int:
    match game_round.my_play:
        case Play.ROCK:
            return 1
        case Play.PAPER:
            return 2
        case Play.SCISSORS:
            return 3
        case _:
            raise Exception("Unknown play: " + str(game_round.my_play))


def score_outcome(game_round: Round) -> int:
    match game_round.opponent_play, game_round.my_play:
        case (Play.ROCK, Play.PAPER) | (Play.PAPER, Play.SCISSORS) | (Play.SCISSORS, Play.ROCK):
            return SCORE_WIN
        case (Play.ROCK, Play.ROCK) | (Play.PAPER, Play.PAPER) | (Play.SCISSORS, Play.SCISSORS):
            return SCORE_DRAW
        case (Play.ROCK, Play.SCISSORS) | (Play.PAPER, Play.ROCK) | (Play.SCISSORS, Play.PAPER):
            return SCORE_LOSE

    raise Exception("Unexpected game: " + str(game_round))


def score_round(game_round: Round) -> int:
    return score_play(game_round) + score_outcome(game_round)


def part1() -> int:
    raw_input = read_input("q2.txt")
    return sum([score_round(parse_round(DecypherStrategy.PRESCRIBED_PLAY, line)) for line in raw_input])


def part2() -> int:
    raw_input = read_input("q2.txt")
    return sum([score_round(parse_round(DecypherStrategy.PRESCRIBED_RESULT, line)) for line in raw_input])
