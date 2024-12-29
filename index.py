import pygame 
import sys
import random
import time
import threading
from collections import deque
from level import start_end
from pygame.locals import *
# Khởi tạo pygame
pygame.init()

# Thiết lập màn hình
screen = pygame.display.set_mode((1500, 800))
pygame.display.set_caption("Game Nối Ống Nước")

# Tao Level
current_level=5
level=0
button_actions = [
    start_end(1),
    start_end(2),
    start_end(3),
    start_end(4),
    start_end(5),
]
# Định nghĩa kích thước ô và lưới
start_pos,end_pos,ROWS,COLS=button_actions[level]
GRID_SIZE = 60
PIPE_SIZE = (60, 60)

# Tải ảnh cho các loại ống
pipe_vertical = pygame.image.load("Pipe_Vertical.png")
pipe_horizontal = pygame.image.load("Pipe_Horizontal.png")
pipe_top_left = pygame.image.load("Pipe_TopLeft.png")
pipe_top_right = pygame.image.load("Pipe_TopRight.png")
pipe_bottom_left = pygame.image.load("Pipe_BottomLeft.png")
pipe_bottom_right = pygame.image.load("Pipe_BottomRight.png")
start_img = pygame.image.load("Start.png")
end_img = pygame.image.load("End.png")

# Thiết lập kích thước các ảnh
pipe_vertical = pygame.transform.scale(pipe_vertical, PIPE_SIZE)
pipe_horizontal = pygame.transform.scale(pipe_horizontal, PIPE_SIZE)
pipe_top_left = pygame.transform.scale(pipe_top_left, PIPE_SIZE)
pipe_top_right = pygame.transform.scale(pipe_top_right, PIPE_SIZE)
pipe_bottom_left = pygame.transform.scale(pipe_bottom_left, PIPE_SIZE)
pipe_bottom_right = pygame.transform.scale(pipe_bottom_right, PIPE_SIZE)
start_img = pygame.transform.scale(start_img, PIPE_SIZE)
end_img = pygame.transform.scale(end_img, PIPE_SIZE)

# Tạo font chữ
font = pygame.font.Font(None, 36)

# Tạo lưới chứa các ống với các vị trí ban đầu
grid = [[{"type": None, "image": None} for _ in range(COLS)] for _ in range(ROWS)]

# Định nghĩa các hướng kết nối cho từng loại ống
pipe_connections = {
    "vertical": {"up": (-1, 0), "down": (1, 0)},
    "horizontal": {"left": (0, -1), "right": (0, 1)},
    "top_left": {"up": (-1, 0), "left": (0, -1)},
    "top_right": {"up": (-1, 0), "right": (0, 1)},
    "bottom_left": {"down": (1, 0), "left": (0, -1)},
    "bottom_right": {"down": (1, 0), "right": (0, 1)},
}



# Tính toán vị trí lưới để nằm giữa màn hình
grid_offset_x = (screen.get_width() - (COLS * GRID_SIZE)) // 2
grid_offset_y = (screen.get_height() - (ROWS * GRID_SIZE)) // 2


#Hàm vẽ lưới và các đoạn ống
def draw_grid():
    screen.fill((46,139,87))# Màu nền 
    for row in range(ROWS):
        for col in range(COLS):
            x = col * GRID_SIZE + grid_offset_x
            y = row * GRID_SIZE + grid_offset_y

            # Hiển thị điểm bắt đầu và kết thúc
            if (row, col) == start_pos:
                screen.blit(start_img, (x, y))
            elif (row, col) == end_pos:
                screen.blit(end_img, (x, y))
            else:
                # Hiển thị các đoạn ống
                pipe = grid[row][col]
                if pipe["image"] is not None:
                    screen.blit(pipe["image"], (x, y))

# Hàm kiểm tra và thay thế loại ống khi click vào
def rotate_pipe_on_click(row, col):
    if (row, col) == start_pos or (row, col) == end_pos:
        return
        # Phát âm thanh khi click
    click_sound.play()
    pipe = grid[row][col]
    
    # Thay đổi hình ảnh tùy theo loại ống
    if pipe["image"] == pipe_vertical:
        pipe["image"] = pipe_horizontal
        pipe["type"] = "horizontal"
    elif pipe["image"] == pipe_horizontal:
        pipe["image"] = pipe_vertical
        pipe["type"] = "vertical"
    elif pipe["image"] == pipe_top_left:
        pipe["image"] = pipe_top_right
        pipe["type"] = "top_right"
    elif pipe["image"] == pipe_top_right:
        pipe["image"] = pipe_bottom_right
        pipe["type"] = "bottom_right"
    elif pipe["image"] == pipe_bottom_right:
        pipe["image"] = pipe_bottom_left
        pipe["type"] = "bottom_left"
    elif pipe["image"] == pipe_bottom_left:
        pipe["image"] = pipe_top_left
        pipe["type"] = "top_left"
    
    update_all_connections()

# Lưu các kết nối giữa các ống
connections = {}
# Hàm cập nhật kết nối của toàn bộ lưới
def update_all_connections():
    global connections
    connections.clear()  # Xóa tất cả kết nối hiện tại

    for row in range(ROWS):
        for col in range(COLS):
            update_connections(row, col)  # Cập nhật kết nối cho từng ô

# Hàm cập nhật kết nối khi thay đổi ống
def update_connections(row, col):
    current_pipe = grid[row][col]
    if current_pipe["image"] is None:
        return

    # Xóa kết nối cũ
    connections.pop((row, col), None)

    # Định nghĩa kết nối đặc biệt cho điểm bắt đầu và điểm kết thúc
    if (row, col) == start_pos:
        new_row, new_col = row, col + 1  # Chỉ kết nối với ô bên phải
        if 0 <= new_row < ROWS and 0 <= new_col < COLS:
            neighbor_pipe = grid[new_row][new_col]
            if neighbor_pipe["type"] in ["horizontal", "top_left", "bottom_left"]:  # Các loại ống phù hợp với điểm bắt đầu
                connections.setdefault((row, col), set()).add((new_row, new_col))
                connections.setdefault((new_row, new_col), set()).add((row, col))
        return

    if (row, col) == end_pos:
        new_row, new_col = row, col - 1  # Chỉ kết nối với ô bên trái
        if 0 <= new_row < ROWS and 0 <= new_col < COLS:
            neighbor_pipe = grid[new_row][new_col]
            if neighbor_pipe["type"] in ["horizontal", "top_right", "bottom_right"]:  # Các loại ống phù hợp với điểm kết thúc
                connections.setdefault((row, col), set()).add((new_row, new_col))
                connections.setdefault((new_row, new_col), set()).add((row, col))
        return

    # Kiểm tra kết nối cho các ống khác
    for direction, (dr, dc) in pipe_connections.get(current_pipe["type"], {}).items():
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < ROWS and 0 <= new_col < COLS:
            neighbor_pipe = grid[new_row][new_col]
            if neighbor_pipe["image"]:
                neighbor_type = neighbor_pipe["type"]
                opposite_direction = {
                    "up": "down",
                    "down": "up",
                    "left": "right",
                    "right": "left"
                }
                if opposite_direction[direction] in pipe_connections.get(neighbor_type, {}):
                    # Tạo kết nối hai chiều giữa hai ô
                    connections.setdefault((row, col), set()).add((new_row, new_col))
                    connections.setdefault((new_row, new_col), set()).add((row, col))
# Hàm kiểm tra xem có đường kết nối từ điểm bắt đầu đến điểm kết thúc không
def check_connection():
    visited = set()
    stack = [start_pos]
    while stack:
        row, col = stack.pop()
        if (row, col) == end_pos:
            return True
        visited.add((row, col))
        
        # Thêm các ô lân cận đã kết nối vào stack
        for neighbor in connections.get((row, col), []):
            if neighbor not in visited:
                stack.append(neighbor)
    
    return False
# Tạo đường ống ban đầu
def initialize_grid():
    for row in range(ROWS):
        for col in range(COLS):
            if (row, col) == start_pos:
                grid[row][col] = {"type": "start", "image": start_img}
            elif (row, col) == end_pos:
                grid[row][col] = {"type": "end", "image": end_img}
            else:
                random_pipe = random.choice([
                    {"image": pipe_vertical, "type": "vertical"},
                    {"image": pipe_horizontal, "type": "horizontal"},
                    {"image": pipe_top_left, "type": "top_left"},
                    {"image": pipe_top_right, "type": "top_right"},
                    {"image": pipe_bottom_left, "type": "bottom_left"},
                    {"image": pipe_bottom_right, "type": "bottom_right"}
                ])
                grid[row][col] = random_pipe

    # Cập nhật kết nối cho toàn bộ lưới
    update_all_connections()

# Khởi tạo lưới với các đoạn ống
initialize_grid()


# Khởi tạo đường đi ngắn nhất
directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
def is_valid_move(x, y, visited):
    return 0 <= x < ROWS and 0 <= y < COLS and not visited[x][y]
# Hàm tìm đường bằng BFS
def bfs(start, end):
    queue = deque([start])
    visited = [[False] * COLS for _ in range(ROWS)]
    visited[start[0]][start[1]] = True
    parent = {start: None}

    while queue:
        current = queue.popleft()
        
        # Kiểm tra nếu đã đến đích
        if current == end:
            break
        random.shuffle(directions)
        for direction in directions:
            next_x, next_y = current[0] + direction[0], current[1] + direction[1]
            if is_valid_move(next_x, next_y, visited):
                visited[next_x][next_y] = True
                queue.append((next_x, next_y))
                parent[(next_x, next_y)] = current
    
    # Tạo đường đi từ đích về bắt đầu
    path = []
    while current is not None:
        path.append(current)
        current = parent[current]
    
    return path[::-1]  # Đảo ngược đường đi


start=(start_pos[0],start_pos[1]+1)
end=(end_pos[0],end_pos[1]-1)
path = bfs(start, end)  # Tìm đường đi
print("Đường đi:", path)  # Xuất ra tọa độ đường đi
def addPipes(path):
    for i in range(1,len(path)):
        x1,y1=path[i-1]
        x2,y2=path[i]
        x3,y3=path[i-2]

        if x1==x2 and y1+1==y2:
            if y1==y3:
                grid[x1][y1]={"image": pipe_bottom_right, "type": "bottom_right"}
            else:
                grid[x1][y1]={"image": pipe_vertical, "type": "vertical"}
        if x1==x2 and y1-1==y2:
            if y1==y3:
                grid[x1][y1]={"image": pipe_bottom_right, "type": "bottom_right"}
            else:
                grid[x1][y1]={"image": pipe_vertical, "type": "vertical"}
        if y1==y2 and x1+1==x2:
            if x1==x3:
                grid[x1][y1]={"image": pipe_bottom_right, "type": "bottom_right"}
            else:
                grid[x1][y1]={"image": pipe_horizontal, "type": "horizontal"}
        if y1==y2 and x1-1==x2:
            if x1==x3:
                grid[x1][y1]={"image": pipe_bottom_right, "type": "bottom_right"}
            else:
                grid[x1][y1]={"image": pipe_horizontal, "type": "horizontal"}
        if start[0]==x1 and start[1]==y1:
            if x2==x1:
                grid[x1][y1]={"image": pipe_vertical, "type": "vertical"}
            else:
                grid[x1][y1]={"image": pipe_bottom_right, "type": "bottom_right"}
            continue
        if end[0]==x2 and end[1]==y2:
            if x2==x1:
                grid[x2][y2]={"image": pipe_vertical, "type": "vertical"}
            else:
                grid[x2][y2]={"image": pipe_bottom_right, "type": "bottom_right"}
            continue
addPipes(path)

# Âm thanh kết nối thành công
success_sound = pygame.mixer.Sound("success.mp3")  # Đường dẫn tới âm thanh
success_sound.set_volume(1.0)

# Khởi tạo nhạc nền
pygame.mixer.init()
pygame.mixer.music.load("background.mp3")  # Thay bằng đường dẫn đến file nhạc
pygame.mixer.music.play(-1)  # Lặp vô hạn
pygame.mixer.music.set_volume(0.4)  # Âm lượng (0.0 đến 1.0)

# Tạo nút bản đồ
screen_width = screen.get_width()
screen_height = screen.get_height()

start_y = 150  # Vị trí bắt đầu theo trục y
button_spacing = 70  # Khoảng cách giữa các nút
button_width = 120
button_height = 40
x_position = screen_width - button_width - 20  # Căn chỉnh sát bên phải (cách lề phải 20px)

buttons = [
    pygame.Rect(x_position, start_y + i * button_spacing, button_width, button_height) for i in range(5)
]

# Hàm vẽ nút
def draw_buttons():
    for i, button in enumerate(buttons):
        pygame.draw.rect(screen, (245, 222, 179), button, border_radius = 15)
        pygame.draw.rect(screen, (0, 0, 0), button, 2 , border_radius = 15)  # Viền đen
        label = font.render(f"Map {i+1}", True, (0,0,0))
        screen.blit(label, (button.x + 25, button.y + 10))



# Biến trạng thái nhạc
music_on = True

# Nút bật/tắt nhạc
music_button = pygame.Rect(screen_width - 1450, screen_height - 730, 50, 50)  # Dạng hình vuông, nút sẽ chuyển thành tròn
speaker_icon = pygame.image.load("speaker.png")  # Đường dẫn tới file hình cái loa
speaker_icon = pygame.transform.scale(speaker_icon, (30, 30))  # Thay đổi kích thước

# Hàm vẽ nút nhạc hình tròn với biểu tượng loa
def draw_music_button():
    # Tọa độ và bán kính của nút nhạc
    center_x, center_y = music_button.center
    radius = music_button.width // 2  # Đường kính là chiều rộng của nút

    # Vẽ hình tròn
    color = (0, 255, 0) if music_on else (255, 0, 0)  # Xanh nếu bật, đỏ nếu tắt
    pygame.draw.circle(screen, color, (center_x, center_y), radius)
    pygame.draw.circle(screen, (0, 0, 0), (center_x, center_y), radius, 2)  # Viền đen

    # Vẽ biểu tượng cái loa 
    if speaker_icon:  # Nếu có tệp hình ảnh loa
        screen.blit(speaker_icon, (center_x - speaker_icon.get_width() // 2, center_y - speaker_icon.get_height() // 2))
    else:  # Nếu không, tự vẽ biểu tượng loa bằng hình học
        pygame.draw.polygon(screen, (0, 0, 0), [
            (center_x - 10, center_y - 15),  # Đỉnh trái
            (center_x - 10, center_y + 15),  # Đỉnh dưới
            (center_x + 10, center_y),       # Đỉnh phải
        ])
        pygame.draw.arc(screen, (0, 0, 0), (center_x - 5, center_y - 15, 30, 30), 0.5, 2.6, 2)  # Sóng loa

    # Hiển thị trạng thái (Music ON/OFF) bên dưới nút
    label = font.render("ON" if music_on else "OFF", True, (30,30,30))
    screen.blit(label, (center_x - label.get_width() // 2, center_y + radius + 5))

# Tải âm thanh hiệu ứng
click_sound = pygame.mixer.Sound("click.mp3")  # Đường dẫn tới file âm thanh
click_sound.set_volume(0.5)  # Đặt âm lượng (0.0 đến 1.0)

# Hàm hiển thị hộp thoại thông báo kết nối thành công
def show_success_dialog():
    # Tạo cửa sổ con để hiển thị thông báo
    dialog_width, dialog_height = 400, 200
    dialog_surface = pygame.Surface((dialog_width, dialog_height))
    dialog_surface.fill((245, 222, 179))  

    # Viền hộp thoại
    pygame.draw.rect(dialog_surface, (0, 0, 0), (0, 0, dialog_width, dialog_height), 5 )

    # Thông báo kết nối thành công
    message = font.render("Kết nối thành công!", True, (0, 128, 0))
    dialog_surface.blit(message, (dialog_width // 2 - message.get_width() // 2, 40))

    # Nút "Chơi tiếp"
    button_width, button_height = 150, 50
    button_x = dialog_width // 2 - button_width // 2
    button_y = dialog_height - button_height - 20
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    pygame.draw.rect(dialog_surface, (0, 200, 0), button_rect, border_radius=15)
    pygame.draw.rect(dialog_surface, (0, 0, 0), button_rect, 2, border_radius=15)

    # Hiển thị chữ trên nút
    button_label = font.render("Chơi tiếp", True, (255, 255, 255))
    dialog_surface.blit(button_label, (button_x + (button_width - button_label.get_width()) // 2, 
                                       button_y + (button_height - button_label.get_height()) // 2))

    # Hiển thị hộp thoại lên màn hình chính
    screen.blit(dialog_surface, ((screen.get_width() - dialog_width) // 2, 
                                 (screen.get_height() - dialog_height) // 2))
    pygame.display.flip()

    # Phát âm thanh thông báo
    success_sound.play()

    # Chờ người dùng bấm "Chơi tiếp"
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                # Kiểm tra xem người dùng bấm vào nút "Chơi tiếp"
                if button_rect.collidepoint(pos[0] - (screen.get_width() - dialog_width) // 2,
                                            pos[1] - (screen.get_height() - dialog_height) // 2):
                    waiting = False  # Thoát khỏi vòng lặp chờ

start_time = pygame.time.get_ticks()
# Vòng lặp game chính
next=True
running = True
while running:

    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

            # Kiểm tra nút nhạc
            if music_button.collidepoint(pos):
                music_on = not music_on
                if music_on:
                    pygame.mixer.music.unpause()
                else:
                    pygame.mixer.music.pause()
            else:
                # Nếu không nhấn vào nút, xử lý xoay ô trong lưới
                row = (pos[1] - grid_offset_y) // GRID_SIZE
                col = (pos[0] - grid_offset_x) // GRID_SIZE
                if 0 <= row < ROWS and 0 <= col < COLS:
                    rotate_pipe_on_click(row, col)
            if check_connection():
                if next:
                    show_success_dialog()
                    next=False
            else:
                next=True

                      
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Chuột trái
            mouse_pos = pygame.mouse.get_pos()  # Lấy vị trí chuột
            for i, button in enumerate(buttons):
                if button.collidepoint(mouse_pos):  # Kiểm tra chuột có nằm trong button không
                    if i+1 <= current_level:  # Chỉ kích hoạt button màn đã được mở
                        level=i
                        start_pos,end_pos,ROWS,COLS=button_actions[level]
                        # Tính toán vị trí lưới để nằm giữa màn hình
                        grid = [[{"type": None, "image": None} for _ in range(COLS)] for _ in range(ROWS)]
                        grid_offset_x = (screen.get_width() - (COLS * GRID_SIZE)) // 2
                        grid_offset_y = (screen.get_height() - (ROWS * GRID_SIZE)) // 2
                        initialize_grid()
                        start=(start_pos[0],start_pos[1]+1)
                        end=(end_pos[0],end_pos[1]-1)
                        path = bfs(start, end)  # Tìm đường đi
                        print("Đường đi:", path)  # Xuất ra tọa độ đường đi
                        addPipes(path)
                        start_time=pygame.time.get_ticks()
                        


# Ví dụ: Thời gian
    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
    time_message = font.render(f"TIME: {elapsed_time}s", True, (0, 0, 0))
   

    # Vẽ mọi thứ
    draw_grid()
    draw_buttons()
    draw_music_button()
    screen.blit(time_message, (10, 10))
    pygame.display.flip()

