from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

img = Image.new("RGB", (2560, 1440), color=(8, 6, 20))
draw = ImageDraw.Draw(img)

draw.ellipse([(-200,-200),(900,900)], fill=(30,20,80))
draw.ellipse([(1700,600),(2800,1700)], fill=(20,50,120))
draw.ellipse([(900,200),(1800,1100)], fill=(15,30,70))

for i in range(0, 2560, 3):
    alpha = 8
    draw.line([(i,0),(i,1440)], fill=(40,40,80,alpha), width=1)

try:
    font_huge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 180)
    font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
    font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 60)
except:
    font_huge = ImageFont.load_default()
    font_big = font_huge
    font_med = font_huge

draw.text((1280, 580), "FogWindowBeats", font=font_huge, fill=(220,210,255), anchor="mm",
          stroke_width=4, stroke_fill=(40,30,100))
draw.text((1280, 760), "lofi music 24/7", font=font_big, fill=(140,120,220), anchor="mm")
draw.text((1280, 880), "Nuevos videos todos los dias - Suscribete!", font=font_med,
          fill=(100,90,180), anchor="mm")

for x, y, r in [(200,200,3),(400,100,2),(600,300,2),(1900,200,3),(2100,350,2),(2300,150,2),
                (300,1200,2),(500,1100,3),(800,1300,2),(1800,1100,3),(2000,1250,2),(2200,1150,2)]:
    draw.ellipse([x-r,y-r,x+r,y+r], fill=(200,180,255,180))

Path("assets").mkdir(exist_ok=True)
img.save("assets/banner.png", "PNG")
print("Banner generado: 2560x1440")