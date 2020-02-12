from collections import defaultdict, Counter

# dump_dir = join_path(ROOT_DIRECTORY, "data/temp_test/dump")  # todo: change this                                                       
# stats_dir = join_path(ROOT_DIRECTORY, "data/temp_test/stats")  # todo: change this                                                     
# extract_from_folder(dump_dir, stats_dir)
# dump_stats = DumpStats(dump_dir, stats_dir)

# Read counting to the dictionary
filename = "projects/affordance/temp.txt"

def read_counts(filename, )
    dict_counter = defaultdict(Counter);
    cond = None;
    with open(filename, "r", encoding='utf-8') as f: 
        # create defaultdict in {condition: {variable: count}} format
        for i, line in enumerate(f): 
            items = line.split()
            num = int(items[1].strip("()"))
            # when the line is a condition
            if items[0][0:3] != "---":
                cond = items[0]
                dict_counter[cond] = Counter({cond: num})
            # when the line is variable
            elif items[0][0:3] == "---":
                var = items[0].strip("-")
                dict_counter[cond].update({var: num})
            else:
                print("%d line is a weird line %s" % (i, line))
            assert cond != None
    return dict_counter