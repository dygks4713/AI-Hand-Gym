import sys
import cv2
import pygame

from game_logic import HandGymGame, HAND_MODES
from hand_detector import HandDetector
from ui import GameUI

WINDOW_SIZE = (1280, 800)
FPS = 30


def main():
    pygame.init()
    pygame.display.set_caption("AI 손가락 체조 게임")
    screen = pygame.display.set_mode(WINDOW_SIZE)
    clock = pygame.time.Clock()

    ui = GameUI(screen)
    game = HandGymGame(total_rounds=10, points_per_round=10, hold_seconds=0.8,
                       countdown_seconds=5, success_seconds=1.5)
    detector = HandDetector()

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not camera.isOpened():
        camera.release()
        camera = cv2.VideoCapture(0)

    camera_ok = camera.isOpened()
    latest_frame = None
    hand_poses = {"Left": None, "Right": None}
    message = "운동 방식을 선택한 후 시작 버튼을 눌러주세요."
    selected_mode = "both"
    running = True

    try:
        while running:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif not game.started and not game.finished:
                        if event.key == pygame.K_1:
                            selected_mode = "both"
                        elif event.key == pygame.K_2:
                            selected_mode = "left"
                        elif event.key == pygame.K_3:
                            selected_mode = "right"
                        elif event.key == pygame.K_SPACE:
                            game.start(selected_mode)
                            message = "5초 후 첫 번째 손동작이 나타납니다."
                    elif event.key == pygame.K_r:
                        game.reset(selected_mode)
                        hand_poses = {"Left": None, "Right": None}
                        message = "시작 버튼을 눌러 게임을 시작하세요."
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not game.started and not game.finished:
                        clicked_mode = ui.menu_mode_at(event.pos)
                        if clicked_mode:
                            selected_mode = clicked_mode
                        elif ui.menu_start_at(event.pos):
                            game.start(selected_mode)
                            message = "5초 후 첫 번째 손동작이 나타납니다."
                    elif game.finished and ui.restart_at(event.pos):
                        game.reset(selected_mode)
                        hand_poses = {"Left": None, "Right": None}
                        message = "시작 버튼을 눌러 게임을 시작하세요."

            if camera_ok:
                success, frame = camera.read()
                if success:
                    frame = cv2.flip(frame, 1)
                    frame, hand_poses = detector.process(frame)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = cv2.resize(frame, (712, 400))
                    latest_frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))

            if game.started and not game.finished:
                if not camera_ok:
                    message = "웹캠 연결을 확인해주세요."
                else:
                    just_scored = game.update(hand_poses["Left"], hand_poses["Right"])
                    if just_scored:
                        message = "성공! 10점을 획득했습니다."
                    elif game.phase == "countdown":
                        message = "다음 동작을 준비해주세요."
                    elif game.phase == "active" and game.target:
                        target_name = game.target["name"]
                        if game.hand_mode == "left":
                            matched = hand_poses["Left"] == game.target_key
                            hand_name = "왼손"
                        elif game.hand_mode == "right":
                            matched = hand_poses["Right"] == game.target_key
                            hand_name = "오른손"
                        else:
                            matched = (hand_poses["Left"] == game.target_key and
                                       hand_poses["Right"] == game.target_key)
                            hand_name = "양손"
                        message = (f"좋아요! {target_name} 동작을 유지해주세요."
                                   if matched else f"{hand_name}으로 {target_name} 동작을 만들어주세요.")
                    elif game.phase == "success":
                        message = "성공! 잠시 후 다음 동작으로 넘어갑니다."

            if not game.started and not game.finished:
                ui.draw_menu(selected_mode, latest_frame, camera_ok)
            else:
                ui.draw(latest_frame, game, hand_poses, message, camera_ok)

    finally:
        camera.release()
        detector.close()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()
