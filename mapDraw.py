from PIL import Image, ImageDraw
import logging

def draw(coordinates,rgblist,x=20,y=20):
    logging.info('Drawing PNG Map')
    img = Image.new('RGB', (1001, 1001), color=(73, 109, 137))
    x_size = 1000/x
    y_size = 1000/y
    iDraw = ImageDraw.Draw(img)

    for i in range(1000,0,-int(y_size)):
       for j in range(0,1001,int(x_size)):
          rgb = (10,10,10)

          coord = [int((j)/x_size)+1,int((1000-i)/y_size)+1]

          if coord in coordinates:
            index = coordinates.index(coord)
            rgb = (rgblist[index][0],rgblist[index][1],rgblist[index][2])

          iDraw.rectangle([(j,i),(j+x_size,i-y_size)],fill=rgb,outline=(255,255,255),width=2)

    logging.info('Saving PNG Map')
    img.save('map.png')