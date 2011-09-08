import csv
import difflib
import sys

def main(argv):
    for f in argv[1:]:
        i = csv.reader(open(f))
        o = csv.writer(sys.stdout)
        for row in i:
            o.writerow(row)

if __name__ == '__main__':
    main(sys.argv)
