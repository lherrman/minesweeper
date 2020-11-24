import numpy as np
import cv2


class MainWindow(object):
    def __init__(self):
        cv2.namedWindow("Minesweeper")
        cv2.setMouseCallback("Minesweeper", self.onMouse)
        self.window_size = 800
        self.board_framebuffer = np.zeros((self.window_size, self.window_size, 3),
                                          dtype=np.uint8)

    def setup_game(self):
        self.board_size = 15
        self.board = np.zeros((self.board_size, self.board_size), dtype=np.int8)
        self.board_animations_state = np.zeros((self.board_size, self.board_size),
                                               dtype=np.int8)
        self.board_user_state = np.zeros((self.board_size, self.board_size),
                                         dtype=np.int8)

        self.tool = 1  # 0 nothing, 1 flags, 2 steps
        self.board_mouse_pos = np.zeros((self.board_size + 1, self.board_size + 1),
                                        dtype=np.int8)
        self.mouse_pos_field = np.zeros(2)
        self.field_width = self.window_size // self.board_size

        self.field_sprite_animation = [self.__create_field_sprite(self.field_width, n) for n in range(self.field_width, 0, -1)]
        self.field_sprite_animation = self.field_sprite_animation[::-1]

        mines = np.random.randint(0, 100, size=(self.board_size, self.board_size))
        padding = np.ones_like(mines) * 100
        padding[2:-2, 2:-2] = mines[2:-2, 2:-2]
        self.mines = (padding < 10).astype(np.uint8)

        self.board_number_hints = np.zeros_like(mines, dtype=np.uint32)

        self.no_mine = np.zeros_like(mines, dtype=np.uint32)
        for x in range(self.board_size):
            for y in range(self.board_size):
                if self.mines[x, y]:
                    rndm = np.random.randint(0, 100, size=4)
                    if self.mines[x + 1, y] == 0:
                        self.no_mine[x + 1, y] += rndm[0]
                    if self.mines[x - 1, y] == 0:
                        self.no_mine[x - 1, y] += rndm[1]
                    if self.mines[x, y + 1] == 0:
                        self.no_mine[x, y + 1] += rndm[2]
                    if self.mines[x, y - 1] == 0:
                        self.no_mine[x, y - 1] += rndm[3]

                self.board_number_hints[x, y] = np.sum(self.mines[x-1:x+2, y-1:y+2])

        self.no_mine = (self.no_mine > 70).astype(np.uint8)

    def draw_board(self):
        self.board_framebuffer *= 0
        for x in range(self.board_size):
            for y in range(self.board_size):
                if self.board_user_state[x, y] and self.board_animations_state[x, y] < self.field_width - 5:
                    self.board_animations_state[x, y] += 4
                elif self.board_user_state[x, y] == 0 and self.board_animations_state[x, y] > 4:
                    self.board_animations_state[x, y] -= 4
                elif self.board_mouse_pos[x, y] and self.board_animations_state[x, y] < 4:
                    self.board_animations_state[x, y] += 1
                elif self.board_animations_state[x, y] > 0 and not self.board_mouse_pos[x, y] and not self.board_user_state[x, y]:
                    self.board_animations_state[x, y] -= 1

                if self.no_mine[x, y]:
                    self.board_framebuffer[x * self.field_width:x * self.field_width + self.field_width,
                                           y * self.field_width:y * self.field_width + self.field_width,
                                           self.board_user_state[x, y]] = self.field_sprite_animation[self.board_animations_state[x, y]]
                if self.mines[x, y]:
                    self.board_framebuffer[x * self.field_width:x * self.field_width + self.field_width,
                                           y * self.field_width:y * self.field_width + self.field_width,
                                           self.board_user_state[x, y]] = self.field_sprite_animation[self.board_animations_state[x, y]]

                if self.board_number_hints[x, y] and self.no_mine[x, y] == 0 and self.mines[x, y] == 0:
                    cv2.putText(self.board_framebuffer, "{}".format(self.board_number_hints[x, y]),
                                (y * self.field_width + self.field_width // 2 - 5, x * self.field_width + self.field_width // 2 + 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))

                if self.board_user_state[x, y] == self.mines[x, y] and self.board_user_state[x, y] == 1:
                    cv2.putText(self.board_framebuffer, "GAME OVER", (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 0, 255))

        cv2.imshow("Minesweeper", self.board_framebuffer)

    def onMouse(self, event, x, y, flags, params):
        global mouseX, mouseY
        if event == cv2.EVENT_MOUSEMOVE:
            self.board_mouse_pos *= 0
            self.mouse_pos_field = [y // self.field_width, x // self.field_width]
            self.board_mouse_pos[y // self.field_width, x // self.field_width] = 1

        if event == cv2.EVENT_LBUTTONDOWN:
            if self.board_user_state[self.mouse_pos_field[0], self.mouse_pos_field[1]] == 0:
                self.board_user_state[self.mouse_pos_field[0], self.mouse_pos_field[1]] = self.tool

            elif self.board_user_state[self.mouse_pos_field[0], self.mouse_pos_field[1]] == 1:
                self.board_user_state[self.mouse_pos_field[0], self.mouse_pos_field[1]] = 0

    def __create_field_sprite(self, width, border=1):
        width_half = width // 2
        field_sprite = np.ones((width, width), dtype=np.uint8) * 255

        roundness = 4
        for x in range(width_half):
            for y in range(width_half):
                if (x**roundness + y**roundness) >= (width_half-border)**roundness:
                    field_sprite[x + width_half, y + width_half] = 0
                    field_sprite[x + width_half, -y + width_half] = 0
                    field_sprite[-x + width_half, y + width_half] = 0
                    field_sprite[-x + width_half, -y + width_half] = 0
        field_sprite_out = np.zeros_like(field_sprite)
        field_sprite_out[1:width - 1, 1:width - 1] = field_sprite[1:width - 1, 1:width - 1]

        return field_sprite_out


if __name__ == "__main__":

    mw = MainWindow()
    mw.setup_game()
    while cv2.waitKey(25) != 27:
        mw.draw_board()
    cv2.destroyAllWindows()
