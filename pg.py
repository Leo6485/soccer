from pygame import *
from pygame.math import Vector2

# Guarda as funções originais
_original_display_set_mode = display.set_mode
_original_draw_rect = draw.rect
_original_draw_circle = draw.circle
_original_blit = Surface.blit
_original_scale = transform.scale
_original_mouse_get_pos = mouse.get_pos
_original_mouse_set_pos = mouse.set_pos

GLOBAL_SCALE = 1

class ScaledScreen:
    def __init__(self, surface, design_resolution, resolution):
        self._surface = surface
        self.design_res = Vector2(design_resolution)
        self.original_resolution = Vector2(resolution)
        self.resolution = Vector2(resolution)
        self.update_scale()
    
    def _s_value(self, value, offset_component=0):
        return int(round(value * self.scale_factor + offset_component))
    
    def _rs_value(self, value, offset_component=0):
        return (value - offset_component) / self.scale_factor
    
    def update_scale(self):
        global GLOBAL_SCALE
        self.resolution = Vector2(self._surface.get_size())
        
        scale_x = self.resolution.x / self.design_res.x
        scale_y = self.resolution.y / self.design_res.y
        self.scale_factor = min(scale_x, scale_y)
        
        GLOBAL_SCALE = self.scale_factor
        self.offset = Vector2(
            (self.resolution.x - (self.design_res.x * self.scale_factor)) / 2,
            (self.resolution.y - (self.design_res.y * self.scale_factor)) / 2
        )
    
    def screen_to_design(self, screen_pos):
        return (
            self._rs_value(screen_pos[0], self.offset.x),
            self._rs_value(screen_pos[1], self.offset.y)
        )
    
    def design_to_screen(self, design_pos):
        return (
            self._s_value(design_pos[0], self.offset.x),
            self._s_value(design_pos[1], self.offset.y)
        )
    
    def __getattr__(self, name):
        return getattr(self._surface, name)
    
    def blit(self, source, dest, area=None, special_flags=0):
        self.update_scale()
        scaled_dest = (
            self._s_value(dest[0], self.offset.x),
            self._s_value(dest[1], self.offset.y)
        )
        
        scaled_source = _original_scale(source, (
            self._s_value(source.get_width()),
            self._s_value(source.get_height())
        ))
        
        scaled_area = None
        if area is not None:
            scaled_area = Rect(
                self._s_value(area[0]),
                self._s_value(area[1]),
                self._s_value(area[2]),
                self._s_value(area[3])
            )
        
        return _original_blit(self._surface, scaled_source, scaled_dest, scaled_area, special_flags)

def s_draw_rect(screen, color, rect, width=0, border_radius=0, **kargs):
    screen.update_scale()
    s_draw_rect = Rect(
        screen._s_value(rect[0], screen.offset.x),
        screen._s_value(rect[1], screen.offset.y),
        screen._s_value(rect[2]),
        screen._s_value(rect[3])
    )
    return _original_draw_rect(screen._surface, color, s_draw_rect, width, border_radius, **kargs)

def s_draw_circle(screen, color, center, radius, width=0):
    screen.update_scale()
    scaled_center = (
        screen._s_value(center[0], screen.offset.x),
        screen._s_value(center[1], screen.offset.y)
    )
    scaled_radius = screen._s_value(radius)
    return _original_draw_circle(screen._surface, color, scaled_center, scaled_radius, width)

def s_mouse_get_pos():
    return Vector2(_original_mouse_get_pos()) / GLOBAL_SCALE

def s_mouse_set_pos(*pos):
    return _original_mouse_set_pos(Vector2(pos) * GLOBAL_SCALE)

draw.rect = s_draw_rect
draw.circle = s_draw_circle
mouse.get_pos = s_mouse_get_pos
mouse.set_pos = s_mouse_set_pos

def set_mode(design_resolution, resolution, flags=0, depth=0):
    actual_screen = _original_display_set_mode(
        resolution,
        flags,
        depth
    )
    return ScaledScreen(actual_screen, design_resolution, resolution)

display.set_mode = set_mode