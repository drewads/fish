import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                                     prog='Literature (Fish) Player',
                                     description='CS 238 Final Project for Drew, Theo, and Tristan that plays the game Literature (https://en.wikipedia.org/wiki/Literature_(card_game))')
    parser.add_argument('--model', type=str, required=True, choices=['simple_rules'])
    args = parser.parse_args()

    if args.model == 'simple_rules':
        from rulestrainer import main
        main()