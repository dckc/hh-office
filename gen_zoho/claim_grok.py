import os

import xlrd

def main(argv):
    d = argv[1]
    for f in os.listdir(d):
        path = os.path.join(d, f)
        book = xlrd.open_workbook(path, formatting_info=True)
        print "worksheets in %s: %d" %(f, book.nsheets)
        print "worksheets in %s: %s" %(f, book.sheet_names())
        print "@@names:", [nob.name for nob in book.name_obj_list], book.name_map, book.name_and_scope_map
        for sheet in book.sheets():
            print "*SHEET: ", sheet.name, sheet.nrows, sheet.ncols
            if 'TEMPLATE' not in sheet.name:
                continue
            
            for rx in range(0, sheet.nrows):
                simple_row = [simple_cell(c) for c in sheet.row(rx)]
                if len([v for v in simple_row
                        if (v is not None and v != u'')]) == 0:
                    continue

                print "*ROW: ", rx
                cx = 0
                for v in simple_row:
                    if v is not None and v != u'':
                        print "%s: [%s]" % (xlrd.cellname(rx, cx), unicode(v).encode('utf-8'))
                        ci = book.font_list[book.xf_list[c.xf_index].font_index].colour_index
                        if ci != 0x7FFF:
                            print "font color: ", ci
                    cx += 1


def simple_cell(cell):
    ctype = cell.ctype
    if ctype == 0:
        return None
    elif ctype in (1, 2):
        return cell.value
    elif ctype == 3:
        raise RuntimeError, 'dates not handled yet'
    elif ctype == 4:
        if cell.value == 1:
            return True
        else:
            return False
    elif ctype == 5:
        return float('nan')
    elif ctype == 6:
        return u''

if __name__ == '__main__':
    import sys
    main(sys.argv)
