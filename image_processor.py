# -*- coding: utf-8 -*-
 
import os
import StringIO
import numpy as np
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

widths = [
  (126,  1), (159,  0), (687,   1), (710,  0), (711,  1),
  (727,  0), (733,  1), (879,   0), (1154, 1), (1161, 0),
  (4347,  1), (4447,  2), (7467,  1), (7521, 0), (8369, 1),
  (8426,  0), (9000,  1), (9002,  2), (11021, 1), (12350, 2),
  (12351, 1), (12438, 2), (12442,  0), (19893, 2), (19967, 1),
  (55203, 2), (63743, 1), (64106,  2), (65039, 1), (65059, 0),
  (65131, 2), (65279, 1), (65376,  2), (65500, 1), (65510, 2),
  (120831, 1), (262141, 2), (1114109, 1),
]


class image_processor:
    def get_width( o ):
        """Return the screen column width for unicode ordinal o."""
        global widths
        if o == 0xe or o == 0xf:
            return 0
        for num, wid in widths:
            if o <= num:
                return wid
        return 1

    def str_to_image( self, str, image_width, save_name ):
        str = unicode(str,'UTF-8')
        font = ImageFont.truetype(os.path.join("fonts", "msyh.ttf"), 12)
        lines = []
        line = ''
        for c in str:
            if font.getsize(line+c)[0] >= image_width-5:
                lines.append(line)
                print line
                line = u''
                line += c 
            else:
                line = line + c
        lines.append( line )
        line_height = font.getsize(str)[1]+3
        img_height = line_height*(len(lines)+1)
        size = (image_width, img_height)
        im = Image.new("RGB", size, (255, 255, 255))
        dr = ImageDraw.Draw(im)
        x,y=5,5
        for line in lines:
            dr.text((x,y),line,font=font,fill="#000000")
            y += line_height
        im.save(save_name)
        return size

    def image_stitching( self, image_paths, positions, save_name, appending ):
        images=[]
        for path in image_paths:
            image = Image.open(path)
            images.append(image)
        p = np.array( positions )
        size = ( np.max(p[:,0]+p[:,2])+appending, np.max(p[:,1]+p[:,3])+appending )
        print size
        target = Image.new( 'RGB', size, (255,255,255) )
        i = 0
        for image in images:
            height = positions[i][3]
            width = positions[i][2]
            temp = image.resize( (width, height), Image.ANTIALIAS )
            target.paste( temp, ( positions[i][0], positions[i][1], positions[i][0]+width, positions[i][1]+height ) )
            i += 1
        target.save( save_name, quality=100 )
        return size