import sqlite3
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
from PIL import ImageFilter

import textwrap


BACKGROUND="background.png"
FONT="Ubuntu Mono"
DATABASE="db.sqlite3"
STARTEP=0
ENDEP=6
FONT="cmunbi.ttf"
EPISODE_NUM_FONT_SIZE=250
EPISODE_NAME_FONT_SIZE=95
MAXTEXTSIZE = (1280-330, 300)
TEXTWRAPWIDTH = 40

conn = sqlite3.connect(DATABASE)
font = ImageFont.truetype(FONT, EPISODE_NUM_FONT_SIZE)

#drop shadow from: http://code.activestate.com/recipes/474116-drop-shadows-with-pil/


def dropShadow( image, offset=(5,5), background=0xffffff, shadow=0x444444, 
                border=8, iterations=3):
  """
  Add a gaussian blur drop shadow to an image.  
  
  image       - The image to overlay on top of the shadow.
  offset      - Offset of the shadow from the image as an (x,y) tuple.  Can be
                positive or negative.
  background  - Background colour behind the image.
  shadow      - Shadow colour (darkness).
  border      - Width of the border around the image.  This must be wide
                enough to account for the blurring of the shadow.
  iterations  - Number of times to apply the filter.  More iterations 
                produce a more blurred shadow, but increase processing time.
  """
  
  # Create the backdrop image -- a box in the background colour with a 
  # shadow on it.
  totalWidth = image.size[0] + abs(offset[0]) + 2*border
  totalHeight = image.size[1] + abs(offset[1]) + 2*border
  back = Image.new(image.mode, (totalWidth, totalHeight), background)
  
  # Place the shadow, taking into account the offset from the image
  shadowLeft = border + max(offset[0], 0)
  shadowTop = border + max(offset[1], 0)
  back.paste(shadow, [shadowLeft, shadowTop, shadowLeft + image.size[0], 
    shadowTop + image.size[1]] )
  
  # Apply the filter to blur the edges of the shadow.  Since a small kernel
  # is used, the filter must be applied repeatedly to get a decent blur.
  n = 0
  while n < iterations:
    back = back.filter(ImageFilter.BLUR)
    n += 1
    
  # Paste the input image onto the shadow backdrop  
  imageLeft = border - min(offset[0], 0)
  imageTop = border - min(offset[1], 0)
  back.paste(image, (imageLeft, imageTop))
  
  return back

for episode in conn.execute("select episodeid, episodename from episode where episodeid between ? and ?", (STARTEP, ENDEP)):
	background = Image.open(BACKGROUND)
	print(episode[0])
	if episode[0] < 10:
		episodeID = "0%s" % (episode[0])
	episodeName = episode[1]
	print("Background file is: ",BACKGROUND, background.format, background.size, background.mode)
	outfile = "thumbnails/Episode%s-thumbnail.png" % (episode[0])
	print(episode, outfile)
	draw = ImageDraw.Draw(background)
	localEpFontSize = EPISODE_NAME_FONT_SIZE
	localTextWrap = TEXTWRAPWIDTH
	textSize = (2000, 2000)

	while (textSize > MAXTEXTSIZE):
		font2 = ImageFont.truetype(FONT, localEpFontSize)

		margin = offset = 40
		imgTemp = Image.new("RGBA", (1,1))
		drawTemp = ImageDraw.Draw(imgTemp)
		totalWidth = 0
		totalHeight = 0

		for line in textwrap.wrap(episodeName, width=localTextWrap):
			width, height = drawTemp.textsize(line, font=font2, fill="#aa0000")
			totalWidth = max(totalWidth , width)
			totalHeight = totalHeight + height	
			print ("innerloop", localTextWrap, localEpFontSize, width, height, totalWidth, totalHeight)
		#textSize = draw.textsize(episodeName, font2)
		

		if (localEpFontSize < 75):
			localTextWrap = localTextWrap - 1
			localEpFontSize = 100

		if (localEpFontSize < 60):
			break

		if ((totalWidth, totalHeight) < MAXTEXTSIZE):
			break
		else:
			localEpFontSize = localEpFontSize - 1


	imgTemp = Image.new("RGBA", (1280,720))
	drawTemp = ImageDraw.Draw(imgTemp)

	shadowImg = Image.new("RGBA", (1280,720))
	shadowDrawTemp = ImageDraw.Draw(shadowImg)

	font2 = ImageFont.truetype(FONT, localEpFontSize)

	margin = 320
	if localTextWrap == 40:
		offset = 520
	else:
		offset = 470		

	for line in textwrap.wrap(episodeName, width=localTextWrap):
		drawTemp.text((margin, offset), line, font=font2, fill="#ffffff")
		shadowDrawTemp.text((margin, offset), line, font=font2, fill="#000000")
		offset += font2.getsize(line)[1]

	#draw.text((353, 513),"%s"% (episodeName),(0,0,0),font=font2)
	#draw.text((350, 510),"%s"% (episodeName),(255,255,255),font=font2)



	#draw.text((98, 513),"%s"% (episodeID),(0,0,0),font=font)
	drawTemp.text((5, 423),"%s"% (episodeID),(255,255,255),font=font)
	shadowDrawTemp.text((5, 420),"%s"% (episodeID),fill="#000000",font=font)

	#background.paste(dropShadow(imgTemp))
	background.paste(shadowImg.filter(ImageFilter.GaussianBlur), box=(3,3), mask=shadowImg.filter(ImageFilter.GaussianBlur))
	background.paste(imgTemp, mask=imgTemp)

	background.save(outfile, "PNG")