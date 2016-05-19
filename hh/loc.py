from sys import argv
import os

def count_loc(lines):
    nb_lines  = 0
    docstring = False
    for line in lines:
        line = line.strip()

        if line == "" \
           or line.startswith("#") \
           or docstring and not (line.startswith('"""') or line.startswith("'''"))\
           or (line.startswith("'''") and line.endswith("'''") and len(line) >3)  \
           or (line.startswith('"""') and line.endswith('"""') and len(line) >3) :
            continue

        # this is either a starting or ending docstring
        elif line.startswith('"""') or line.startswith("'''"):
            docstring = not docstring
            continue

        else:
            nb_lines += 1

    return nb_lines

if __name__ == "__main__":
    files = [f for f in os.listdir(".") if "loc." not in f and f.endswith(".py")]
    program_files = [f for f in files if "test_" not in f]
    test_files = [f for f in files if "test_" in f]

    def print_loc(file_list):
        total_lines = 0
        for f in file_list:
            lines = count_loc(open(f).readlines())
            print("%s: %d" % (f, lines))
            total_lines += lines
        print("\nTotal lines: %d" % total_lines)

    print("=============")
    print("Program files:")
    print("=============")
    print_loc(program_files)
    print("\n")
    print("=============")
    print("Test files:")
    print("=============")
    print_loc(test_files)
