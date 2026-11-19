import random
import time

GESTURES = {
    "fist": {
        "name": "주먹",
        "emoji": "✊",
        "instruction": "손가락을 모두 오므려 주먹을 쥐세요."
    },
    "palm": {
        "name": "손바닥",
        "emoji": "✋",
        "instruction": "손가락을 활짝 펴서 손바닥을 보여주세요."
    },
    "v_sign": {
        "name": "브이",
        "emoji": "✌️",
        "instruction": "검지와 중지를 펴고 나머지 손가락은 접어주세요."
    },
}

HAND_MODES = {
    "both": {
        "name": "양손", 
        "description": "왼손과 오른손을 모두 사용합니다."
    },
    "left": {
        "name": "왼손", 
        "description": "왼손만 사용합니다."
    },
    "right": {
        "name": "오른손", 
        "description": "오른손만 사용합니다."
    },
}


class HandGymGame:
    """5초 준비 카운트다운과 성공 안내를 포함한 손 체조 게임 상태 관리."""

    def __init__(self, total_rounds=10, points_per_round=10, hold_seconds=0.8,
                 countdown_seconds=5, success_seconds=1.5):
        self.total_rounds = total_rounds
        self.points_per_round = points_per_round
        self.hold_seconds = hold_seconds
        self.countdown_seconds = countdown_seconds
        self.success_seconds = success_seconds
        self.reset()

    def reset(self, hand_mode="both"):
        self.hand_mode = hand_mode if hand_mode in HAND_MODES else "both"
        
        # 직전 동작과 중복되지 않도록 무작위 출제
        gestures = list(GESTURES.keys())
        self.sequence = []

        for i in range(self.total_rounds):
            if i == 0:
                # 첫 라운드는 3가지 동작 중 무작위 선택
                next_gesture = random.choice(gestures)
            else:
                # 직전 라운드 동작을 제외한 2가지 중 무작위 선택
                available_gestures = [
                    gesture for gesture in gestures
                    if gesture != self.sequence[-1]
                ]
                next_gesture = random.choice(available_gestures)
            self.sequence.append(next_gesture)

        self.round_index = 0
        self.score = 0
        self.started = False
        self.finished = False
        self.phase = "ready"
        self.phase_started = None
        self.start_time = None
        self.finish_time = None
        self.correct_since = None

    def start(self, hand_mode=None):
        if hand_mode is not None:
            self.hand_mode = hand_mode
        self.reset(self.hand_mode)
        self.started = True
        self.start_time = time.monotonic()
        self._begin_countdown()

    def _begin_countdown(self):
        self.phase = "countdown"
        self.phase_started = time.monotonic()
        self.correct_since = None

    @property
    def countdown_remaining(self):
        if self.phase != "countdown":
            return 0
        remaining = self.countdown_seconds - (time.monotonic() - self.phase_started)
        return max(0, int(remaining + 0.999))

    @property
    def target_key(self):
        if self.phase != "active" or self.finished:
            return None
        return self.sequence[self.round_index]

    @property
    def target(self):
        key = self.target_key
        return GESTURES.get(key) if key else None

    @property
    def elapsed_seconds(self):
        if self.start_time is None:
            return 0.0
        end = self.finish_time if self.finished else time.monotonic()
        return max(0.0, end - self.start_time)

    @property
    def hold_progress(self):
        if self.correct_since is None or self.phase != "active":
            return 0.0
        return min(1.0, (time.monotonic() - self.correct_since) / self.hold_seconds)

    def _required_pose_matches(self, left_pose, right_pose, target):
        if self.hand_mode == "left":
            return left_pose == target
        if self.hand_mode == "right":
            return right_pose == target
        return left_pose == target and right_pose == target

    def update(self, left_pose, right_pose):
        """선택한 손 모드에 맞춰 목표 동작 성공 여부를 갱신한다."""
        if not self.started or self.finished:
            return False

        now = time.monotonic()
        if self.phase == "countdown":
            if now - self.phase_started >= self.countdown_seconds:
                self.phase = "active"
                self.phase_started = now
            return False

        if self.phase == "success":
            if now - self.phase_started >= self.success_seconds:
                if self.round_index >= self.total_rounds:
                    self.finished = True
                    self.phase = "finished"
                    self.finish_time = now
                else:
                    self._begin_countdown()
            return False

        if self.phase != "active":
            return False

        target = self.target_key
        if not self._required_pose_matches(left_pose, right_pose, target):
            self.correct_since = None
            return False

        if self.correct_since is None:
            self.correct_since = now
            return False

        if now - self.correct_since >= self.hold_seconds:
            self.score += self.points_per_round
            self.round_index += 1
            self.correct_since = None
            self.phase = "success"
            self.phase_started = now
            return True
        return False
