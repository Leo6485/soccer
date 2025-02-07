from pygame import *

scale = 0.5

original_draw_rect = draw.rect
original_draw_circle = draw.circle
original_draw_ellipse = draw.ellipse
original_draw_polygon = draw.polygon
original_draw_line = draw.line
original_draw_lines = draw.lines
original_draw_arc = draw.arc
original_draw_image = transform.scale

draw.rect = lambda screen, color, rect, width=0: original_draw_rect(screen, color, Rect(rect.left * scale, rect.top * scale, rect.width * scale, rect.height * scale), int(width * scale))
draw.circle = lambda screen, color, pos, size: original_draw_circle(screen, color, (int(pos[0] * scale), int(pos[1] * scale)), size * scale)
draw.ellipse = lambda screen, color, rect, width=0: original_draw_ellipse(screen, color, Rect(rect.left * scale, rect.top * scale, rect.width * scale, rect.height * scale), int(width * scale))
draw.polygon = lambda screen, color, points, width=0: original_draw_polygon(screen, color, [(int(x * scale), int(y * scale)) for x, y in points], int(width * scale))
draw.line = lambda screen, color, start_pos, end_pos, width=1: original_draw_line(screen, color, (int(start_pos[0] * scale), int(start_pos[1] * scale)), (int(end_pos[0] * scale), int(end_pos[1] * scale)), int(width * scale))
draw.lines = lambda screen, color, closed, points, width=1: original_draw_lines(screen, color, closed, [(int(x * scale), int(y * scale)) for x, y in points], int(width * scale))
draw.arc = lambda screen, color, rect, start_angle, stop_angle, width=1: original_draw_arc(screen, color, Rect(rect.left * scale, rect.top * scale, rect.width * scale, rect.height * scale), start_angle, stop_angle, int(width * scale))
transform.scale = lambda image, size: original_draw_image(image, (int(size[0] * scale), int(size[1] * scale)))

original_font = font.Font
font.Font = lambda font, size: original_font(font, int(size * scale))