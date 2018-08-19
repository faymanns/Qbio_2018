import json
import argh
import os.path

def main(directory):
    directory = os.path.expanduser(os.path.expandvars(directory))
    with open(os.path.join(directory, 'position.json'), 'r') as fp:
            position_dict = json.load(fp)
    for i in (0, 1, 2, 3):
        if position_dict[f'slot_{i}']['left_wall'] > 20:
            print(directory, f'slot_{i} left_wall is ', position_dict[f'slot_{i}']['left_wall'])
        if position_dict[f'slot_{i}']['laser'] > 430 or position_dict[f'slot_{i}']['laser'] < 370:
            print(directory, f'slot_{i} laser is ', position_dict[f'slot_{i}']['laser'])
        if position_dict[f'slot_{i}']['right_wall'] < 810:
            print(directory, f'slot_{i} right_wall is ', position_dict[f'slot_{i}']['right_wall'])
    
if __name__ == '__main__':
    argh.dispatch_command(main)
