"""학습 진행도 관리 모듈.

챕터별 문제 풀이 현황, 퀴즈 점수, 연속 학습 스트릭을 추적한다.
JSON 파일 기반 영속 저장소를 사용한다.
"""

import json
from datetime import date, timedelta
from pathlib import Path


# 저장 경로: 프로젝트 루트의 data/progress.json
_PROGRESS_FILE = Path(__file__).parent.parent / "data" / "progress.json"


def _load_progress() -> dict:
    """진행도 데이터를 파일에서 로드한다.

    파일이 없으면 기본 구조를 반환한다.

    Returns:
        dict: 진행도 데이터 딕셔너리
    """
    if _PROGRESS_FILE.exists():
        try:
            with open(_PROGRESS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    return _default_progress()


def _save_progress(data: dict) -> None:
    """진행도 데이터를 파일에 저장한다.

    Args:
        data: 저장할 진행도 딕셔너리
    """
    _PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(_PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _default_progress() -> dict:
    """기본 진행도 데이터 구조를 반환한다."""
    return {
        "solved_problems": {},
        "quiz_scores": {},
        "daily_log": [],
        "last_active_date": None,
        "streak_days": 0,
    }


class ProgressManager:
    """학습 진행도 관리 클래스.

    문제 풀이 기록, 퀴즈 점수, 연속 학습 스트릭을 관리한다.

    Example:
        >>> pm = ProgressManager()
        >>> pm.mark_problem_solved("ch5_p01", score=1.0, hints_used=0)
        >>> stats = pm.get_overall_stats()
    """

    CHAPTER_PROBLEM_COUNTS = {1: 15, 2: 15, 3: 15, 4: 15, 5: 15, 6: 15, 7: 15, 8: 15}
    CHAPTER_QUIZ_COUNTS = {1: 10, 2: 10, 3: 10, 4: 10, 5: 10, 6: 10, 7: 10, 8: 10}

    def __init__(self):
        """ProgressManager를 초기화하고 진행도 데이터를 로드한다."""
        self._data = _load_progress()

    def mark_problem_solved(
        self,
        problem_id: str,
        score: float,
        hints_used: int = 0,
        attempts: int = 1,
    ) -> None:
        """문제를 풀었음을 기록한다.

        Args:
            problem_id: 문제 ID (예: "ch5_p01")
            score: 획득 점수 (0.0 ~ 1.0)
            hints_used: 사용한 힌트 수
            attempts: 시도 횟수
        """
        existing = self._data["solved_problems"].get(problem_id, {})
        old_score = existing.get("score", 0.0)

        self._data["solved_problems"][problem_id] = {
            "solved": score >= 1.0,
            "score": max(old_score, score),
            "attempts": existing.get("attempts", 0) + attempts,
            "hints_used": hints_used,
            "date": str(date.today()),
        }

        self._update_daily_log()
        _save_progress(self._data)

    def mark_quiz_answered(self, question_id: str, correct: bool) -> None:
        """퀴즈 문제 답변을 기록한다.

        Args:
            question_id: 퀴즈 문제 ID
            correct: 정답 여부
        """
        self._data["quiz_scores"][question_id] = correct
        _save_progress(self._data)

    def get_chapter_completion(self, chapter_id: int) -> float:
        """챕터의 문제 완료율을 반환한다 (0.0 ~ 1.0).

        Args:
            chapter_id: 챕터 번호 (1~8)

        Returns:
            float: 완료율
        """
        total = self.CHAPTER_PROBLEM_COUNTS.get(chapter_id, 15)
        prefix = f"ch{chapter_id}_p"

        solved = sum(
            1
            for pid, info in self._data["solved_problems"].items()
            if pid.startswith(prefix) and info.get("solved", False)
        )

        return solved / total if total > 0 else 0.0

    def get_chapter_quiz_score(self, chapter_id: int) -> float:
        """챕터 퀴즈 점수를 반환한다 (0.0 ~ 1.0).

        Args:
            chapter_id: 챕터 번호

        Returns:
            float: 퀴즈 정답률
        """
        total = self.CHAPTER_QUIZ_COUNTS.get(chapter_id, 10)
        prefix = f"ch{chapter_id}_q"

        correct = sum(
            1
            for qid, is_correct in self._data["quiz_scores"].items()
            if qid.startswith(prefix) and is_correct
        )

        return correct / total if total > 0 else 0.0

    def get_overall_stats(self) -> dict:
        """전체 학습 통계를 반환한다.

        Returns:
            dict: solved_problems, total_problems, overall_completion,
                  streak_days, daily_solved, chapter_completions 포함
        """
        total_problems = sum(self.CHAPTER_PROBLEM_COUNTS.values())
        solved = sum(
            1
            for info in self._data["solved_problems"].values()
            if info.get("solved", False)
        )

        today = str(date.today())
        daily_solved = sum(
            1
            for info in self._data["solved_problems"].values()
            if info.get("date") == today and info.get("solved", False)
        )

        chapter_completions = {
            ch_id: self.get_chapter_completion(ch_id)
            for ch_id in range(1, 9)
        }

        return {
            "solved_problems": solved,
            "total_problems": total_problems,
            "overall_completion": solved / total_problems if total_problems > 0 else 0.0,
            "streak_days": self._data.get("streak_days", 0),
            "daily_solved": daily_solved,
            "chapter_completions": chapter_completions,
        }

    def get_problem_status(self, problem_id: str) -> dict:
        """특정 문제의 풀이 상태를 반환한다.

        Args:
            problem_id: 문제 ID

        Returns:
            dict: 상태 정보 (solved, score, attempts, hints_used)
        """
        return self._data["solved_problems"].get(
            problem_id,
            {"solved": False, "score": 0.0, "attempts": 0, "hints_used": 0},
        )

    def _update_daily_log(self) -> None:
        """오늘 날짜를 학습 로그에 추가하고 스트릭을 갱신한다."""
        today = str(date.today())

        if today not in self._data["daily_log"]:
            self._data["daily_log"].append(today)

        self._data["streak_days"] = self._calculate_streak()
        self._data["last_active_date"] = today

    def _calculate_streak(self) -> int:
        """연속 학습 일수를 계산한다.

        Returns:
            int: 연속 학습 일수
        """
        if not self._data["daily_log"]:
            return 0

        log_dates = sorted(set(self._data["daily_log"]), reverse=True)
        today = date.today()
        streak = 0

        for i, date_str in enumerate(log_dates):
            try:
                log_date = date.fromisoformat(date_str)
                expected = today - timedelta(days=i)
                if log_date == expected:
                    streak += 1
                else:
                    break
            except ValueError:
                continue

        return streak

    def reset_progress(self) -> None:
        """모든 진행도를 초기화한다."""
        self._data = _default_progress()
        _save_progress(self._data)

    def export_progress(self) -> str:
        """진행도 데이터를 JSON 문자열로 내보낸다.

        Returns:
            str: JSON 형식의 진행도 데이터
        """
        return json.dumps(self._data, ensure_ascii=False, indent=2)

    def import_progress(self, json_str: str) -> bool:
        """JSON 문자열에서 진행도를 가져온다.

        Args:
            json_str: JSON 형식의 진행도 데이터

        Returns:
            bool: 성공 여부
        """
        try:
            data = json.loads(json_str)
            required_keys = {"solved_problems", "quiz_scores", "daily_log"}
            if not required_keys.issubset(data.keys()):
                return False

            self._data = data
            _save_progress(self._data)
            return True
        except (json.JSONDecodeError, Exception):
            return False
