#!/usr/bin/env python

import os
import argparse
import Image
import StringIO

template = """<!DOCTYPE html>
<html>
  <head>
    <style type="text/css">
      td { width:%(cell_size)spx; height:%(cell_size)spx; }
%(css)s
    </style>
  </head>
  <body>

    <table border="0" cellpadding="0" cellspacing="0">
%(table)s
    </table>

  </body>
</html>
"""

def tablify(path, max_size=None, cell_size=1, indent=0):
    """ Turn an image into a table! """

    indent = ' ' * indent
    newline = '\n' if indent else ''

    with open(path, 'rb') as f:
        img = Image.open(f).convert('RGB')
        size = img.size

        # Resize, if necessary
        if max_size is not None:
            if size[0] > max_size and size[0] >= size[1]:
                resize = True
                size = (max_size, int(round((float(max_size) / size[0]) * size[1])))
            elif size[1] > max_size:
                resize = True
                size = (int(round((float(max_size) / size[1]) * size[0])), max_size)
            else:
                resize = False
            if resize:
                img = img.resize(size, Image.BICUBIC)

        html = StringIO.StringIO()
        colors = {}

        # Create a table cell for each pixel
        for y in xrange(size[1]):
            row = '%s<tr>%s' % (indent * 3, newline)
            for x in xrange(size[0]):
                # Only store each color once
                color = img.getpixel((x, y))
                color_key = colors.get(color)
                if color_key is None:
                    color_key = 'c%s' % len(colors.keys())
                    colors[color] = color_key
                row += '%s<td class=%s></td>%s' % (indent * 4, color_key, newline)
            html.write('%s%s</tr>%s' % (indent * 3, row, newline))

        # Convert unique colors to CSS classes
        color_css = StringIO.StringIO()
        for c in colors.items():
            if len(c[0]) > 3:
                mode = 'rgba'
                c = (c[0][:3] + (100 * c[0][3] / 255.0,), c[1])
            else:
                mode = 'rgb'
            color_css.write('%s.%s{background-color:%s%s}%s' % (indent * 3, c[1], mode, c[0], newline))

        result = StringIO.StringIO(template % {
            'cell_size': cell_size,
            'css': color_css.getvalue(),
            'table': html.getvalue(),
        })

        html.close()
        color_css.close()

        return result

def main():
    parser = argparse.ArgumentParser(description='Convert an image to an HTML table.')
    parser.add_argument('path', metavar='PATH', help='Image path')
    parser.add_argument('--max-size', dest='max_size', type=int, help='Max image size (width and height)')
    parser.add_argument('--cell-size', dest='cell_size', type=int, default=1, help='Table cell width and height (default: 1)')
    parser.add_argument('--format', dest='format', action='store_true', default=False, help='Format the resulting HTML')
    args = parser.parse_args()
    out_path = '%s.html' % '.'.join(os.path.basename(args.path).split('.')[:-1])
    with open(out_path, 'w') as out:
        out.write(tablify(args.path, max_size=args.max_size, cell_size=args.cell_size, indent=2 if args.format else 0).getvalue())

if __name__ == '__main__':
    main()
