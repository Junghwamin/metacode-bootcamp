"""데이터 파일 무결성 테스트."""

import json
import os
import pytest


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


class TestChapterData:
    """챕터 데이터 JSON 테스트."""

    @pytest.mark.parametrize("chapter_id", range(1, 9))
    def test_chapter_json_valid(self, chapter_id):
        """각 챕터 JSON이 유효해야 한다."""
        path = os.path.join(DATA_DIR, "chapters", f"chapter{chapter_id}.json")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["chapter_id"] == chapter_id
        assert "title" in data
        assert "sections" in data
        assert len(data["sections"]) >= 3

    @pytest.mark.parametrize("chapter_id", range(1, 9))
    def test_problems_json_has_15(self, chapter_id):
        """각 챕터에 15개 문제가 있어야 한다."""
        path = os.path.join(DATA_DIR, "problems", f"chapter{chapter_id}_problems.json")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["chapter_id"] == chapter_id
        assert len(data["problems"]) == 15

    @pytest.mark.parametrize("chapter_id", range(1, 9))
    def test_problems_have_required_fields(self, chapter_id):
        """각 문제에 필수 필드가 있어야 한다."""
        path = os.path.join(DATA_DIR, "problems", f"chapter{chapter_id}_problems.json")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for p in data["problems"]:
            assert "problem_id" in p
            assert "title" in p
            assert "difficulty" in p
            assert p["difficulty"] in ("basic", "intermediate", "advanced")
            assert "description" in p
            assert "initial_code" in p
            assert "solution_code" in p
            assert "hints" in p
            assert "grading" in p
            assert "method" in p["grading"]

    @pytest.mark.parametrize("chapter_id", range(1, 9))
    def test_problems_difficulty_distribution(self, chapter_id):
        """각 챕터에 기초/중급/심화가 각 5개씩 있어야 한다."""
        path = os.path.join(DATA_DIR, "problems", f"chapter{chapter_id}_problems.json")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        difficulties = [p["difficulty"] for p in data["problems"]]
        assert difficulties.count("basic") == 5
        assert difficulties.count("intermediate") == 5
        assert difficulties.count("advanced") == 5

    @pytest.mark.parametrize("chapter_id", range(1, 9))
    def test_quiz_json_valid(self, chapter_id):
        """각 챕터 퀴즈가 유효해야 한다."""
        path = os.path.join(DATA_DIR, "quizzes", f"chapter{chapter_id}_quiz.json")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["chapter_id"] == chapter_id
        assert "questions" in data
        assert len(data["questions"]) >= 5

    @pytest.mark.parametrize("chapter_id", range(1, 9))
    def test_quiz_questions_have_required_fields(self, chapter_id):
        """각 퀴즈 문제에 필수 필드가 있어야 한다."""
        path = os.path.join(DATA_DIR, "quizzes", f"chapter{chapter_id}_quiz.json")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for q in data["questions"]:
            assert "question_id" in q
            assert "type" in q
            assert q["type"] in ("multiple_choice", "ox", "fill_blank")
            assert "question" in q
            assert "correct_answer" in q
            assert "explanation" in q
