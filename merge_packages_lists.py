#!/usr/bin/python


import os, sys, json






def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

def main():

    new = dict()
    new["packages_list"] = list()
    new["packages"] = dict()
    for js in sys.argv[1:-1]:
        with open(js) as config_file:
            config = json.load(config_file)
            new["packages_list"].append(config["packages_list"])
            new["packages"] = merge_two_dicts(new["packages"], config["packages"])

    with open(sys.argv[-1], 'w') as outfile:
        json.dump(new, outfile,indent = 4,)


if __name__ == '__main__':
    main()
