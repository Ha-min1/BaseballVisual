import pygame
import sys

# 초기화
pygame.init()
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("야구 경기 기록판")
clock = pygame.time.Clock()

# 색상 정의
BLACK = (18, 18, 18)
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
RED = (220, 20, 60)
YELLOW = (255, 215, 0)
GRAY = (230, 230, 230)
BLUE = (30, 144, 255)
DARK_GRAY = (60, 60, 60)
ORANGE = (255, 140, 0)
LIGHT_BLUE = (173, 216, 230)
TRANSPARENT_GRAY = (30, 30, 30, 180)

# 게임 상태
class BaseballGame:
    def __init__(self):
        self.reset_game()
    
    def reset_game(self):
        self.inning = 1
        self.top_bottom = "TOP"  # 'TOP'/'BOT'으로 표기
        self.score = [0, 0]  # [홈팀, 어웨이]
        self.outs = 0
        self.strikes = 0
        self.balls = 0
        self.bases = [False, False, False]  # 1루, 2루, 3루
    
    def advance_runners(self, bases):
        new_bases = [False, False, False]
        for i in range(3):
            if self.bases[i]:
                new_pos = i + bases
                if new_pos < 3:
                    new_bases[new_pos] = True
                else:
                    self.score[1 if self.top_bottom == "TOP" else 0] += 1
        if bases < 4:
            new_bases[bases - 1] = True
        else:
            self.score[1 if self.top_bottom == "TOP" else 0] += 1
        self.bases = new_bases
    
    def handle_hit(self, hit_type):
        hit_types = {1: 1, 2: 2, 3: 3, 4: 4}
        self.advance_runners(hit_types[hit_type])
        self.strikes = 0
        self.balls = 0
    
    def handle_pitch(self, is_strike):
        if is_strike:
            self.strikes += 1
            if self.strikes >= 3:
                self.outs += 1
                self.strikes = 0
                self.balls = 0
        else:
            self.balls += 1
            if self.balls >= 4:
                self.advance_runners(1)
                self.strikes = 0
                self.balls = 0
        if self.outs >= 3:
            self.switch_inning()
    
    def switch_inning(self):
        self.outs = 0
        self.strikes = 0
        self.balls = 0
        self.bases = [False, False, False]
        if self.top_bottom == "TOP":
            self.top_bottom = "BOT"
        else:
            self.top_bottom = "TOP"
            self.inning += 1

game = BaseballGame()
def draw_rounded_rect(surface, color, rect, radius=15):
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def draw_baseball_field():
    # 그라운드
    pygame.draw.ellipse(screen, GREEN, (120, 120, 660, 480))
    # 다이아몬드
    diamond = [(450, 320 + 150), (570, 220 + 150), (450, 120 + 150), (330, 220 + 150)]
    pygame.draw.polygon(screen, WHITE, diamond, 5)
    # 베이스
    base_pos = [(450, 320 + 150), (570, 220 + 150), (450, 120 + 150), (330, 220 + 150)]
    for i, (x, y) in enumerate(base_pos[1:]):
        color = YELLOW if game.bases[i] else WHITE
        pygame.draw.circle(screen, color, (x, y), 17)
        pygame.draw.circle(screen, BLACK, (x, y), 17, 2)
    # 홈플레이트
    pygame.draw.polygon(screen, RED, [
        (450, 320 + 150), (440, 335 + 150), (450, 340 + 150), (460, 335 + 150)
    ])
    pygame.draw.polygon(screen, BLACK, [
        (450, 320 + 150), (440, 335 + 150), (450, 340 + 150), (460, 335 + 150)
    ], 2)
    # 마운드
    pygame.draw.circle(screen, LIGHT_BLUE, (450, 220 + 150), 22)
    pygame.draw.circle(screen, BLUE, (450, 220 + 150), 22, 2)


def draw_scoreboard():
    # 반투명 박스
    s = pygame.Surface((370, 170), pygame.SRCALPHA)
    draw_rounded_rect(s, (40, 40, 40, 220), (0, 0, 370, 170), 20)
    screen.blit(s, (35, 35))

    # 팀명 및 점수
    big_font = pygame.font.SysFont(None, 52, bold=True)
    team_font = pygame.font.SysFont(None, 36)
    score_font = pygame.font.SysFont(None, 48, bold=True)
    inning_font = pygame.font.SysFont(None, 36, bold=True)
    
    # 팀명
    home = team_font.render("HOME", True, WHITE)
    away = team_font.render("AWAY", True, WHITE)
    screen.blit(home, (60, 55))
    screen.blit(away, (60, 105))
    # 점수
    home_score = score_font.render(str(game.score[0]), True, BLUE)
    away_score = score_font.render(str(game.score[1]), True, ORANGE)
    screen.blit(home_score, (170, 50))
    screen.blit(away_score, (170, 100))
    # 이닝
    inning_str = f"Inning {game.inning} {game.top_bottom}"
    inning = inning_font.render(inning_str, True, YELLOW)
    screen.blit(inning, (240, 65))
    # 아웃, 스트라이크, 볼
    draw_count_circles(70, 155)

def draw_count_circles(x, y):
    # 아웃(빨강), 스트라이크(파랑), 볼(초록)
    out_font = pygame.font.SysFont(None, 28, bold=True)
    # i*90로 레이블 간 간격 확대
    labels = [("O", RED, game.outs, 3), ("S", BLUE, game.strikes, 3), ("B", GREEN, game.balls, 4)]
    for i, (label, color, count, max_count) in enumerate(labels):
        l = out_font.render(label, True, color)
        screen.blit(l, (x + i*92, y))  
        # 원 간격도 22로 넓힘
        for j in range(max_count):
            cx = x + i*90 + 35 + j*22
            cy = y + 12
            fill = color if j < count else DARK_GRAY
            pygame.draw.circle(screen, fill, (cx, cy), 8)
            pygame.draw.circle(screen, WHITE, (cx, cy), 8, 2)

def draw_controls():
    # 하단 컨트롤 안내
    s = pygame.Surface((WIDTH, 40), pygame.SRCALPHA)
    draw_rounded_rect(s, (30, 30, 30, 180), (0, 0, WIDTH, 40), 0)
    screen.blit(s, (0, HEIGHT - 50))
    font = pygame.font.SysFont(None, 26)
    controls = [
        "1-4: Hit", "S: Strike", "B: Ball",
        "F: Fly Out", "G: Ground Out", "R: Reset"
    ]
    for i, control in enumerate(controls):
        t = font.render(control, True, WHITE)
        screen.blit(t, (30 + i*140, HEIGHT - 40))

# 메인 루프
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1: game.handle_hit(1)
            elif event.key == pygame.K_2: game.handle_hit(2)
            elif event.key == pygame.K_3: game.handle_hit(3)
            elif event.key == pygame.K_4: game.handle_hit(4)
            elif event.key == pygame.K_s: game.handle_pitch(True)
            elif event.key == pygame.K_b: game.handle_pitch(False)
            elif event.key == pygame.K_f: 
                game.outs += 1
                if game.outs >= 3: game.switch_inning()
            elif event.key == pygame.K_g: 
                game.outs += 1
                if game.outs >= 3: game.switch_inning()
            elif event.key == pygame.K_r: game.reset_game()
    
    screen.fill(BLACK)
    draw_baseball_field()
    draw_scoreboard()
    draw_controls()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

