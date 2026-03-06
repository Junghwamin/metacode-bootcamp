"""단계별 힌트 시스템.

보상 프레이밍: 힌트 미사용 시 +20% 보너스 점수.
3단계 힌트 모두 사용 후에도 막히면 '정답 보기' + '건너뛰기' 탈출구 제공.

설계 원칙:
- 힌트 0개 사용: 보너스 +20% (도전 의욕 촉진)
- 힌트 1개 사용: 기본 점수 유지 (정직한 시도 인정)
- 힌트 2~3개 사용: 점수 감점 (힌트 남발 억제)
- 3번 힌트 + 5회 이상 시도: 정답 공개 탈출구 제공 (학습 포기 방지)
"""


class HintSystem:
    """단계별 힌트 제공 시스템.

    보상 프레이밍 방식으로 힌트 사용 수에 따라 점수 배율을 조정한다.
    총 3단계 힌트를 제공하며, 모두 소진 후 일정 시도 횟수 이상이면
    정답 보기 옵션을 활성화한다.

    Class Attributes:
        BONUS_RATE (float): 힌트 미사용 시 보너스 배율 (0.2 = +20%)
        MAX_HINT_LEVELS (int): 최대 힌트 단계 수 (3단계)
        ANSWER_REVEAL_ATTEMPTS (int): 정답 공개 활성화 최소 시도 횟수 (5회)

    Example:
        >>> hs = HintSystem()
        >>> hint = hs.get_hint(problem, level=1)
        >>> multiplier = hs.get_score_multiplier(hints_used=1)
        >>> print(hs.get_hint_status_text(hints_used=0))
        힌트를 사용하지 않으면 보너스 점수 +20%!
    """

    # 힌트 미사용 보너스 비율 (1.0 + BONUS_RATE = 1.2배)
    BONUS_RATE = 0.2

    # 최대 힌트 단계 수
    MAX_HINT_LEVELS = 3

    # 정답 공개 활성화를 위한 최소 시도 횟수
    ANSWER_REVEAL_ATTEMPTS = 5

    def get_hint(self, problem: dict, level: int) -> str | None:
        """지정 레벨의 힌트를 반환한다.

        problem 딕셔너리의 "hints" 리스트에서 level에 해당하는 힌트를 꺼낸다.
        힌트는 1-indexed (level 1 = hints[0]).

        Args:
            problem: 문제 딕셔너리. "hints" 키에 문자열 리스트 포함.
                     예: {"hints": ["첫 번째 힌트", "두 번째 힌트", "세 번째 힌트"]}
            level: 힌트 레벨 (1, 2, 3). 범위 밖이면 None 반환.

        Returns:
            str | None: 힌트 문자열 또는 해당 레벨 힌트가 없으면 None
        """
        if level < 1 or level > self.MAX_HINT_LEVELS:
            return None

        hints = problem.get("hints", [])

        # level은 1-indexed이므로 hints[level - 1]
        hint_index = level - 1
        if hint_index >= len(hints):
            return None

        hint_text = hints[hint_index]
        return hint_text if hint_text else None

    def get_score_multiplier(self, hints_used: int) -> float:
        """힌트 사용 개수에 따른 점수 배율을 반환한다.

        보상 프레이밍 핵심 로직:
        - 0개 사용: 1.2 (보너스 +20%로 도전 의욕 촉진)
        - 1개 사용: 1.0 (기본 점수 유지, 합리적 힌트 사용 허용)
        - 2개 사용: 0.9 (약간 감점, 과도한 힌트 의존 억제)
        - 3개 사용: 0.7 (감점 강화, 모든 힌트 소진 페널티)

        Args:
            hints_used: 사용한 힌트 개수 (0~3)

        Returns:
            float: 점수 배율 (0.7 ~ 1.2)
        """
        multiplier_table = {
            0: 1.0 + self.BONUS_RATE,  # 1.2 (보너스)
            1: 1.0,                     # 1.0 (기본)
            2: 0.9,                     # 0.9 (소폭 감점)
            3: 0.7,                     # 0.7 (감점)
        }

        # 정의된 범위 밖이면 경계값으로 클램핑
        if hints_used <= 0:
            return multiplier_table[0]
        elif hints_used >= self.MAX_HINT_LEVELS:
            return multiplier_table[self.MAX_HINT_LEVELS]
        else:
            return multiplier_table.get(hints_used, 1.0)

    def get_hint_status_text(self, hints_used: int) -> str:
        """UI에 표시할 힌트 사용 상태 텍스트를 반환한다.

        현재 힌트 사용 상태를 사용자에게 명확하게 전달하여
        보상 프레이밍의 효과를 극대화한다.

        Args:
            hints_used: 사용한 힌트 개수 (0~3)

        Returns:
            str: 한국어 상태 텍스트
        """
        status_texts = {
            0: "힌트를 사용하지 않으면 보너스 점수 +20%!",
            1: "힌트 1개 사용 중 (기본 점수)",
            2: "힌트 2개 사용 중 (점수 90%)",
            3: "힌트 3개 사용 (점수 70%)",
        }

        if hints_used <= 0:
            return status_texts[0]
        elif hints_used >= self.MAX_HINT_LEVELS:
            return status_texts[self.MAX_HINT_LEVELS]
        else:
            return status_texts.get(hints_used, status_texts[0])

    def should_show_answer(self, hints_used: int, attempts: int) -> bool:
        """정답 보기 버튼 활성화 여부를 반환한다.

        힌트를 모두 소진하고 충분한 횟수를 시도한 학습자에게
        탈출구를 제공하여 학습 포기를 방지한다.

        조건: 힌트 3개 모두 사용 AND 시도 횟수 >= 5회

        Args:
            hints_used: 사용한 힌트 개수
            attempts: 총 제출 시도 횟수

        Returns:
            bool: True이면 '정답 보기' 및 '건너뛰기' 버튼 표시
        """
        # 모든 힌트 소진 + 최소 시도 횟수 이상
        all_hints_used = hints_used >= self.MAX_HINT_LEVELS
        enough_attempts = attempts >= self.ANSWER_REVEAL_ATTEMPTS

        return all_hints_used and enough_attempts

    def get_solution(self, problem: dict) -> str:
        """문제의 정답 코드를 반환한다.

        정답 공개는 should_show_answer()가 True일 때만 호출해야 한다.
        problem 딕셔너리에 "solution" 키가 없으면 안내 메시지를 반환한다.

        Args:
            problem: 문제 딕셔너리. "solution" 키에 정답 코드 문자열 포함.

        Returns:
            str: 정답 코드 문자열. "solution" 키가 없으면 안내 메시지.
        """
        solution = problem.get("solution", "")

        if not solution:
            return "# 이 문제의 정답 코드가 아직 준비되지 않았습니다."

        return solution

    def get_available_hint_levels(self, problem: dict) -> list[int]:
        """해당 문제에서 사용 가능한 힌트 레벨 목록을 반환한다.

        문제에 실제로 정의된 힌트 수만큼 레벨을 반환한다.
        UI에서 힌트 버튼 표시 여부 결정에 사용한다.

        Args:
            problem: 문제 딕셔너리. "hints" 키에 힌트 리스트 포함.

        Returns:
            list[int]: 사용 가능한 힌트 레벨 번호 리스트 (예: [1, 2, 3])
        """
        hints = problem.get("hints", [])
        # 비어 있지 않은 힌트만 레벨 계산
        available = [
            level
            for level in range(1, self.MAX_HINT_LEVELS + 1)
            if (level - 1) < len(hints) and hints[level - 1]
        ]
        return available

    def get_remaining_hints(self, problem: dict, hints_used: int) -> int:
        """아직 사용하지 않은 힌트 수를 반환한다.

        UI에서 "힌트 N개 남음" 텍스트 표시에 사용한다.

        Args:
            problem: 문제 딕셔너리
            hints_used: 이미 사용한 힌트 개수

        Returns:
            int: 남은 힌트 수 (0 이상)
        """
        available = len(self.get_available_hint_levels(problem))
        remaining = max(0, available - hints_used)
        return remaining
