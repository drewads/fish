import argparse


valid_models = ['simple_rules']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                                     description='CS 238 Final Project for Drew, Theo, and Tristan that plays the game Literature (https://en.wikipedia.org/wiki/Literature_(card_game))')
    parser.add_argument('--model', type=str, required=True, choices=valid_models)
    parser.add_argument('--baseline_model', type=str, required=False, choices=valid_models, default='simple_rules')
    args = parser.parse_args()

    if args.model == 'simple_rules':
        from rulestrainer import play_game
        play_game()