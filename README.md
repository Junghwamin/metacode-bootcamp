# 메타코드 Python 부트캠프

메타코드 "파이썬 기초 이론 PPT자료" 기반 인터랙티브 Python 학습 플랫폼

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://metacode-bootcamp-bdsypgjnef5wgazhfsvje6.streamlit.app/)
[![CI/CD](https://github.com/Junghwamin/metacode-bootcamp/actions/workflows/ci.yml/badge.svg)](https://github.com/Junghwamin/metacode-bootcamp/actions)

## 바로 시작하기

**[여기를 클릭하면 바로 실습할 수 있습니다](https://metacode-bootcamp-bdsypgjnef5wgazhfsvje6.streamlit.app/)**

설치, 회원가입, 로그인 필요 없음 — 브라우저만 있으면 됩니다.

## 주요 기능

- **8챕터 개념 학습** — Python 기초부터 NumPy/Pandas까지
- **120개 실습 문제** — 챕터당 15문제 (기초 5 + 중급 5 + 고급 5)
- **코드 에디터 & 실행** — 브라우저에서 직접 코드 작성 및 실행
- **자동 채점** — 8가지 채점 방식 (출력 비교, 변수 검증, 함수 호출 등)
- **단계별 힌트** — 3단계 힌트 + 힌트 미사용 시 보너스 점수
- **한국어 에러 번역** — Python 에러 메시지를 초보자 친화적 한국어로 변환
- **80개 퀴즈** — 객관식, O/X, 빈칸 채우기
- **진행도 저장** — 브라우저에 자동 저장 (개인별 독립)

## 챕터 구성

| 챕터 | 주제 | 문제 | 퀴즈 |
|------|------|------|------|
| 1 | Python 시작하기 | 15 | 10 |
| 2 | 데이터 타입 | 15 | 10 |
| 3 | 자료형 (List, Tuple, Set, Dict) | 15 | 10 |
| 4 | 조건문과 반복문 | 15 | 10 |
| 5 | 함수와 클래스 | 15 | 10 |
| 6 | 파일 다루기 | 15 | 10 |
| 7 | 예외 처리 | 15 | 10 |
| 8 | 라이브러리 (NumPy, Pandas) | 15 | 10 |

## 여러 명이 동시에 써도 되나요?

**네, 됩니다.** 진행도와 학습 데이터는 각자의 **브라우저 localStorage**에 저장됩니다.

- 같은 링크로 접속해도 각자의 진행도는 독립적
- 서버에 개인정보가 저장되지 않음
- 다른 기기/브라우저에서 접속하면 진행도가 초기화됨 (내보내기/가져오기 기능으로 이동 가능)

## 로컬 실행 (선택사항)

```bash
git clone https://github.com/Junghwamin/metacode-bootcamp.git
cd metacode-bootcamp
pip install -r requirements.txt
streamlit run app.py
```

## 기술 스택

- **Frontend**: Streamlit, streamlit-code-editor
- **코드 실행**: subprocess 격리 (AST 보안 검증)
- **데이터**: JSON 기반 (24개 파일)
- **CI/CD**: GitHub Actions (flake8 + pytest + JSON 검증)
