import argparse
from rulestrainer import main

valid_models = ['simple_rules']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='CS 238 Final Project for Drew, Theo, and Tristan that \
                     plays the game Literature \
                     (https://en.wikipedia.org/wiki/Literature_(card_game))'
    )
    parser.add_argument('--model_count', type=int, required=False, default=0)
    parser.add_argument('--csv_name', type=str, required=False, default='model_data.csv')
    args = parser.parse_args()

    main(args.csv_name, args.model_count)