
import cv2
import mediapipe as mp
import math


class HandDetector:
    """
    MediaPipe Hands로 양손을 검출하고
    주먹, 손바닥, 브이 동작을 분류한다.

    엄지는 판별에 사용하지 않는다.
    손바닥과 손등 방향에 관계없이
    네 손가락의 관절 각도를 기준으로 분류한다.
    """

    def __init__(
        self,
        max_hands=2,
        detection_confidence=0.65,
        tracking_confidence=0.60
    ):
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            model_complexity=1,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )

    @staticmethod
    def _angle(a, b, c):
        """
        2차원 좌표를 이용해 b 지점의 관절 각도를 계산한다.
        손바닥 또는 손등 방향에 따른 z 좌표 영향을 받지 않는다.
        """

        ba = (a.x - b.x, a.y - b.y)
        bc = (c.x - b.x, c.y - b.y)

        dot = ba[0] * bc[0] + ba[1] * bc[1]

        norm_ba = math.hypot(*ba)
        norm_bc = math.hypot(*bc)

        if norm_ba == 0 or norm_bc == 0:
            return 0

        cosine = dot / (norm_ba * norm_bc)
        cosine = max(-1.0, min(1.0, cosine))

        return math.degrees(math.acos(cosine))

    def classify(self, landmarks):
        """
        손가락 관절 각도로 손동작을 분류한다.

        반환값:
        fist, palm, v_sign, None
        """

        # 검지, 중지, 약지, 새끼손가락
        finger_data = [
            (5, 6, 7),       # 검지: MCP, PIP, DIP
            (9, 10, 11),     # 중지
            (13, 14, 15),    # 약지
            (17, 18, 19),    # 새끼
        ]

        extended = []
        folded = []

        for mcp_idx, pip_idx, dip_idx in finger_data:

            mcp = landmarks[mcp_idx]
            pip = landmarks[pip_idx]
            dip = landmarks[dip_idx]

            # PIP 관절의 각도
            angle = self._angle(mcp, pip, dip)

            # 손가락이 펴진 상태
            is_extended = angle >= 150

            # 손가락이 접힌 상태
            is_folded = angle <= 135

            extended.append(is_extended)
            folded.append(is_folded)

        index = extended[0]
        middle = extended[1]
        ring = extended[2]
        pinky = extended[3]

        # -----------------------------
        # 1. 손바닥
        # -----------------------------

        if all(extended):
            return "palm"

        # -----------------------------
        # 2. 브이
        # -----------------------------

        if (
            index
            and middle
            and folded[2]
            and folded[3]
        ):
            return "v_sign"

        # -----------------------------
        # 3. 주먹
        # -----------------------------

        if all(folded):
            return "fist"

        # 명확하게 구분되지 않는 자세
        return None

    def process(self, bgr_frame):
        """
        입력 영상은 좌우 반전된 프레임이어야 한다.
        """

        rgb = cv2.cvtColor(
            bgr_frame,
            cv2.COLOR_BGR2RGB
        )

        results = self.hands.process(rgb)

        detected = {
            "Left": None,
            "Right": None
        }

        if results.multi_hand_landmarks:

            handedness_list = results.multi_handedness or []

            for index, hand_landmarks in enumerate(
                results.multi_hand_landmarks
            ):

                self.mp_draw.draw_landmarks(
                    bgr_frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                )

                label = "Unknown"

                if index < len(handedness_list):
                    label = (
                        handedness_list[index]
                        .classification[0].label
                    )

                if label in detected:
                    detected[label] = self.classify(
                        hand_landmarks.landmark
                    )

        return bgr_frame, detected

    def close(self):
        self.hands.close()
