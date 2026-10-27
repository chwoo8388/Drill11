import math
import time

from pico2d import (
    SDL_KEYDOWN,
    SDL_KEYUP,
    SDL_QUIT,
    SDLK_LEFT,
    SDLK_RIGHT,
    SDLK_UP,
    SDLK_a,
    load_image,
)
from transitions import Machine


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.is_moving = False
        self.auto_running = False
        self.pressed_keys = set()
        self.ground_y = self.y
        self.jump_velocity = 0
        self.is_jumping = False
        self.started_at = time.monotonic()
        self.is_lying = False
        self.image = load_image('animation_sheet.png')
        self.machine = Machine(
            model=self,
            states=['IDLE'],
            transitions=[{
                'trigger': 'advance_idle_frame',
                'source': 'IDLE',
                'dest': 'IDLE',
                'after': '_advance_idle_frame',
            }],
            initial='IDLE',
            auto_transitions=False,
        )

    def update(self):
        now = time.monotonic()
        if self.pressed_keys or self.is_jumping or self.auto_running:
            self.started_at = now
            self.is_lying = False
        elif now - self.started_at >= 5:
            self.is_lying = True
        if self.is_lying:
            return

        move_x = 1 if self.auto_running else (
            int(SDLK_RIGHT in self.pressed_keys) - int(SDLK_LEFT in self.pressed_keys)
        )
        self.is_moving = move_x != 0 or self.is_jumping
        self.x += move_x * 5
        if move_x != 0:
            self.face_dir = 1 if move_x > 0 else -1

        if self.is_jumping:
            self.y += self.jump_velocity
            self.jump_velocity -= 0.6
            if self.y <= self.ground_y:
                self.y = self.ground_y
                self.jump_velocity = 0
                self.is_jumping = False

        self.advance_idle_frame()

    def handle_event(self, event):
        if event.type != SDL_QUIT:
            self.is_lying = False
            self.started_at = time.monotonic()
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_a:
                self.auto_running = True
            if event.key in (SDLK_LEFT, SDLK_RIGHT, SDLK_UP):
                is_new_press = event.key not in self.pressed_keys
                self.pressed_keys.add(event.key)
                if event.key == SDLK_UP and is_new_press and not self.is_jumping:
                    self.is_jumping = True
                    self.jump_velocity = 12
        elif event.type == SDL_KEYUP:
            self.pressed_keys.discard(event.key)

    def _advance_idle_frame(self):
        self.frame = (self.frame + 1) % 8

    def draw(self):
        if self.is_lying:
            self.image.clip_composite_draw(
                self.frame * 100, 300 if self.face_dir == 1 else 200,
                100, 100, -math.pi / 2, '', self.x, self.y, 100, 100,
            )
            return
        row = 100 if self.is_moving else 300
        if self.face_dir == -1:
            row -= 100
        self.image.clip_draw(self.frame * 100, row, 100, 100, self.x, self.y)