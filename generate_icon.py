from PIL import Image, ImageDraw

# Create 256x256 image with smooth gradient/glow
size = (256, 256)
img = Image.new("RGBA", size, (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Outer rounded badge
draw.rounded_rectangle([10, 10, 246, 246], radius=48, fill=(225, 29, 72, 255), outline=(244, 63, 94, 255), width=6)
# Inner dark core
draw.rounded_rectangle([28, 28, 228, 228], radius=38, fill=(17, 18, 29, 255))

# Play icon / Film symbol
# Triangle play button pointing right
triangle = [(100, 75), (185, 128), (100, 181)]
draw.polygon(triangle, fill=(244, 63, 94, 255))

# Loop arrow circle around it
draw.arc([60, 60, 196, 196], start=45, end=315, fill=(56, 189, 248, 255), width=10)
# Arrow head
arrow = [(196, 120), (216, 138), (180, 148)]
draw.polygon(arrow, fill=(56, 189, 248, 255))

# Save multi-size ICO
img.save("app_icon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("Icon generated successfully!")
