import os
import pygame
from game_logic import GESTURES, HAND_MODES


BG = (22, 29, 40)
PANEL = (34, 44, 59)
PANEL_LIGHT = (43, 56, 73)
WHITE = (245, 247, 250)
MUTED = (177, 190, 204)
GREEN = (58, 190, 137)
YELLOW = (255, 202, 90)
RED = (239, 110, 110)


def find_korean_font():
    candidates = [
        os.path.join("assets", "fonts", "malgun.ttf"),
        r"C:\Windows\Fonts\malgun.ttf",
        r"C:\Windows\Fonts\malgunsl.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


class GameUI:
    def __init__(self, screen):
        self.screen = screen
        font_path = find_korean_font()
        self.font = pygame.font.Font(font_path, 27)
        self.small = pygame.font.Font(font_path, 20)
        self.medium = pygame.font.Font(font_path, 34)
        self.large = pygame.font.Font(font_path, 58)
        self.huge = pygame.font.Font(font_path, 82)

        # 이모티콘 전용 폰트
        self.emoji_font = pygame.font.SysFont(
            "Segoe UI Emoji",
            self.huge.get_height()
        )

    def text(self, value, x, y, font=None, color=WHITE, center=False):
        surface = (font or self.font).render(str(value), True, color)
        rect = surface.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.screen.blit(surface, rect)

    def wrapped_text(self, value, x, y, max_width, font=None,
                     color=WHITE, line_spacing=8):
        font = font or self.font
        words = str(value)
        lines = []
        current_line = ""

        for char in words:
            test_line = current_line + char

            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char
        
        if current_line:
            lines.append(current_line)

        line_height = font.get_linesize() + line_spacing

        for i, line in enumerate(lines):
            self.text(line, x, y + i * line_height, font, color)

    def panel(self, rect, color=PANEL, radius=20):
        pygame.draw.rect(self.screen, color, rect, border_radius=radius)

    def menu_mode_rect(self, mode):
        return pygame.Rect({"both": 100, "left": 455, "right": 810}[mode], 300, 320, 190)

    def menu_mode_at(self, position):
        for mode in ("both", "left", "right"):
            if self.menu_mode_rect(mode).collidepoint(position):
                return mode
        return None

    @staticmethod
    def menu_start_rect():
        return pygame.Rect(440, 515, 400, 82)

    def menu_start_at(self, position):
        return self.menu_start_rect().collidepoint(position)

    @staticmethod
    def restart_at(position):
        return pygame.Rect(440, 570, 400, 70).collidepoint(position)

    def draw_menu(self, selected_mode, camera_surface=None, camera_ok=True):
        self.screen.fill(BG)
        self.panel((50, 35, 1180, 205))
        self.text("AI 손가락 체조 게임", 640, 95, self.huge, WHITE, center=True)
        self.text("원하는 운동 방식을 선택해주세요.", 640, 180, self.medium, MUTED, center=True)

        descriptions = {
            "both": ("양손 운동", "왼손과 오른손을 함께 사용"),
            "left": ("왼손 운동", "왼손만 사용"),
            "right": ("오른손 운동", "오른손만 사용"),
        }
        for mode in ("both", "left", "right"):
            rect = self.menu_mode_rect(mode)
            selected = mode == selected_mode
            color = (42, 91, 76) if selected else PANEL
            self.panel(rect, color, 22)
            if selected:
                pygame.draw.rect(self.screen, GREEN, rect, 4, border_radius=22)
            title, description = descriptions[mode]
            self.text(title, rect.centerx, rect.y + 62, self.large,
                      GREEN if selected else WHITE, center=True)
            self.text(description, rect.centerx, rect.y + 130, self.small,
                      WHITE if selected else MUTED, center=True)
            self.text({"both": "1", "left": "2", "right": "3"}[mode] + "번 키",
                      rect.centerx, rect.y + 166, self.small, YELLOW, center=True)

        start_rect = self.menu_start_rect()
        self.panel(start_rect, GREEN, 22)
        self.text("게임 시작하기", start_rect.centerx, start_rect.centery,
                  self.medium, (15, 35, 29), center=True)

        # 시작 버튼 아래에 어르신도 쉽게 따라 할 수 있는 조작 안내 표시
        guide_rect = pygame.Rect(90, 615, 1100, 165)
        self.panel(guide_rect, PANEL, 18)
        self.text("게임을 시작하는 방법", 640, 638, self.font, YELLOW, center=True)

        key_rect = pygame.Rect(125, 665, 210, 66)
        pygame.draw.rect(self.screen, PANEL_LIGHT, key_rect, border_radius=12)
        pygame.draw.rect(self.screen, YELLOW, key_rect, 2, border_radius=12)
        self.text("SPACE 바", key_rect.centerx, key_rect.centery,
                  self.medium, YELLOW, center=True)

        self.text("키보드 아래쪽에 있는 긴 스페이스 바를 한 번 눌러주세요.",
                  365, 672, self.small, WHITE)
        self.text("초록색 '게임 시작하기' 버튼을 마우스로 눌러도 시작할 수 있습니다.",
                  365, 708, self.small, WHITE)
        self.text("시작하면 5초 동안 준비한 뒤, 화면에 나오는 손동작을 따라 하시면 됩니다.",
                  365, 744, self.small, MUTED)

        if not camera_ok:
            self.text("카메라를 찾을 수 없습니다. 웹캠 연결을 확인하세요.",
                      640, 790, self.small, RED, center=True)
        pygame.display.flip()

    def draw(self, camera_surface, game, hand_poses, message, camera_ok=True):
        self.screen.fill(BG)

        # Header / score
        self.panel((24, 20, 1232, 116))
        self.text(f"AI 손가락 체조 - {HAND_MODES[game.hand_mode]['name']} 모드", 50, 38, self.medium)
        self.text("획득 점수", 770, 34, self.small, MUTED)
        self.text(f"{game.score} / 100", 770, 62, self.large, GREEN)
        self.text(f"라운드  {game.round_index} / 10", 1030, 67, self.font)

        # Progress bar
        pygame.draw.rect(self.screen, PANEL_LIGHT, (50, 151, 1180, 16), border_radius=8)
        progress_width = int(1180 * game.score / 100)
        if progress_width:
            pygame.draw.rect(self.screen, GREEN, (50, 151, progress_width, 16), border_radius=8)

        # Camera panel
        self.panel((24, 190, 760, 540))
        self.text("실시간 손동작 인식", 48, 208, self.font)
        camera_rect = pygame.Rect(48, 255, 712, 400)
        if camera_surface is not None:
            scaled = pygame.transform.smoothscale(camera_surface, camera_rect.size)
            self.screen.blit(scaled, camera_rect)
        else:
            self.panel(camera_rect, (12, 17, 24), 12)
            self.text("카메라 화면을 불러오는 중입니다.", 404, 450,
                      self.small, MUTED, center=True)

        # Right panel / target
        self.panel((804, 190, 442, 540))
        self.text("지금 따라 할 동작", 828, 212, self.font, MUTED)

        target = game.target
        if target:
            self.text(target["emoji"], 1025, 330, self.emoji_font, WHITE, center=True)
            self.text(target["name"], 1025, 410, self.large, YELLOW, center=True)
            self.wrapped_text(target["instruction"], 830, 465, 370, self.small, WHITE, line_spacing=10)
        elif game.finished:
            self.text("🏆", 1025, 340, self.huge, GREEN, center=True)
            self.text("게임 완료!", 1025, 430, self.large, GREEN, center=True)
        elif game.phase == "countdown":
            self.text("준비하세요!", 1025, 330, self.large, YELLOW, center=True)
            self.text(str(game.countdown_remaining), 1025, 425, self.huge, WHITE, center=True)
            self.text("다음 동작이 곧 나타납니다.", 1025, 500, self.small, MUTED, center=True)
        elif game.phase == "success":
            self.text("성공!", 1025, 350, self.huge, GREEN, center=True)
            self.text("10점을 획득했습니다.", 1025, 455, self.font, WHITE, center=True)
        else:
            self.text("준비 완료", 1025, 360, self.large, WHITE, center=True)
            self.text("스페이스바를 눌러 시작하세요", 1025, 425,
                      self.small, MUTED, center=True)

        # Hand statuses
        self.panel((828, 525, 394, 112), PANEL_LIGHT, 14)
        left_pose = hand_poses.get("Left")
        right_pose = hand_poses.get("Right")
        if game.hand_mode == "left":
            self.text("왼손 (사용)", 850, 542, self.small, MUTED)
            self.text(GESTURES[left_pose]["name"] if left_pose in GESTURES else "인식 대기",
                      850, 574, self.font, GREEN if left_pose else YELLOW)
            self.text("오른손 (미사용)", 1040, 542, self.small, MUTED)
            self.text("사용 안 함", 1040, 574, self.font, MUTED)
        elif game.hand_mode == "right":
            self.text("왼손 (미사용)", 850, 542, self.small, MUTED)
            self.text("사용 안 함", 850, 574, self.font, MUTED)
            self.text("오른손 (사용)", 1040, 542, self.small, MUTED)
            self.text(GESTURES[right_pose]["name"] if right_pose in GESTURES else "인식 대기",
                      1040, 574, self.font, GREEN if right_pose else YELLOW)
        else:
            self.text("왼손", 850, 542, self.small, MUTED)
            self.text(GESTURES[left_pose]["name"] if left_pose in GESTURES else "인식 대기",
                      850, 574, self.font, GREEN if left_pose else YELLOW)
            self.text("오른손", 1040, 542, self.small, MUTED)
            self.text(GESTURES[right_pose]["name"] if right_pose in GESTURES else "인식 대기",
                      1040, 574, self.font, GREEN if right_pose else YELLOW)

        # Footer
        elapsed = game.elapsed_seconds
        mins, secs = divmod(int(elapsed), 60)
        self.text(f"진행 시간  {mins:02d}:{secs:02d}", 50, 752, self.font)
        self.text(message, 440, 752, self.small, GREEN if "성공" in message or "축하" in message else MUTED)
        self.text("R: 다시하기   ESC: 종료", 850, 752, self.small, MUTED)

        if not camera_ok:
            self.text("카메라를 찾을 수 없습니다. 웹캠 연결을 확인하세요.",
                      640, 700, self.small, RED, center=True)

        if game.phase == "success" and not game.finished:
            self.panel((390, 285, 500, 220), (25, 65, 52), 24)
            self.text("성공!", 640, 355, self.huge, GREEN, center=True)
            self.text("10점을 획득했습니다.", 640, 435, self.medium, WHITE, center=True)

        if game.finished:
            self.panel((350, 245, 580, 370), (25, 48, 43), 24)
            self.text("축하합니다!", 640, 300, self.large, GREEN, center=True)
            self.text("100점 달성!", 640, 380, self.huge, WHITE, center=True)
            self.text(f"총 소요 시간  {mins:02d}분 {secs:02d}초",
                      640, 475, self.medium, YELLOW, center=True)
            self.text("R 키를 누르면 모드 선택 화면으로 돌아갑니다.", 640, 550,
                      self.small, MUTED, center=True)

        pygame.display.flip()