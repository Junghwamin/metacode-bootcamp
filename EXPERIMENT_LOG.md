# 실험 로그 (Experiment Log)

## 2026-03-07: 프로젝트 초기 구축

### 변경 내용
- 프로젝트 디렉토리 구조 생성
- Streamlit 설정 파일 (config.toml) 작성
- requirements.txt 의존성 정의
- 코어 모듈, UI 모듈, 테스트 모듈 초기화

### 설계 결정
- **코드 실행**: subprocess 프로세스 격리 방식 채택 (exec+threading 대비 보안 강화)
- **보안**: AST 기반 SecurityValidator로 dunder 속성 접근 사전 차단
- **코드 에디터**: streamlit-code-editor 사용 (streamlit-ace 비활성 상태로 교체)
- **진행도**: streamlit-local-storage + 2-pass 로딩 패턴
- **힌트**: 보상 프레이밍 (힌트 미사용 시 +20% 보너스)

---

## 2026-03-07: 채점/힌트/진행도 모듈 구현

### 변경 내용
- `core/grader.py` 신규 생성: 8가지 채점 방식 지원 자동 채점기
- `core/hint_system.py` 신규 생성: 보상 프레이밍 힌트 시스템
- `core/progress.py` 신규 생성: 2-pass localStorage 진행도 관리

### 구현 세부 사항

#### core/grader.py
- `GradeMethod` Enum: EXACT_OUTPUT, REGEX_OUTPUT, VARIABLE_CHECK, FUNCTION_EXISTS, FUNCTION_CALL, CLASS_CHECK, MULTI_TESTCASE, NUMERIC_OUTPUT
- `GradeResult` dataclass: passed, score(0.0~1.0), total_tests, passed_tests, feedback(한국어), details
- `Grader` 클래스: problem["grading"]["method"] 기반 자동 라우팅
- 부분 점수: VARIABLE_CHECK(맞은 변수/전체), FUNCTION_CALL(통과 케이스/전체), CLASS_CHECK(클래스 30% + 메서드 30% + TC 40%)
- MULTI_TESTCASE: 합산 타임아웃 10초 (per_case = 10/n초)
- NUMERIC_OUTPUT: epsilon(기본 1e-6) 절대 오차 허용
- f-string 내 `!r[:N]` 슬라이싱 호환성 이슈 수정 (repr() 분리 처리)

#### core/hint_system.py
- 배율 테이블: 힌트 0개→1.2, 1개→1.0, 2개→0.9, 3개→0.7
- `should_show_answer()`: 힌트 3개 소진 + 5회 이상 시도 시 정답 공개
- `get_available_hint_levels()`: 문제별 실제 정의된 힌트 수 기반 레벨 반환
- `get_remaining_hints()`: UI용 남은 힌트 수 계산

#### core/progress.py
- 스키마 버전 "1.0": version, chapters(1~8), streak_days, daily_solved 등
- 2-pass 로딩: "loading" → "loaded"/"error" 상태 머신
- `update_problem()`: best_score 최고값 보존, last_code 5000자 제한, 자동 동기화
- `update_streak()`: 전날 학습→연속 증가, 2일+ 공백→1로 리셋
- `export_progress()` / `import_progress()`: JSON 직렬화 + 스키마 검증
- graceful fallback: streamlit-local-storage 미설치 시 session_state만으로 동작

### 개선점
- 이전 대비: 채점/힌트/진행도 코어 모듈 부재 → 완전 구현
- 한국어 피드백으로 학습자 경험 향상
- 부분 점수 지원으로 OOP 문제 등 복잡한 채점 가능

---

## 2026-03-07: UI 모듈 구현

### 변경 내용
- `ui/theme.py` 신규 생성 (528줄)
  - THEME 색상 팔레트 + DIFFICULTY_LABELS 정의
  - `apply_theme()`: Noto Sans KR 폰트, 난이도 배지, 코드 에디터, 진행도 바, 버튼(실행/제출/초기화), 모바일 반응형(@media 768px), 폰트 크기 조절 CSS 주입
  - `set_font_size()`: session_state 기반 폰트 크기 설정 (small/medium/large)

- `ui/onboarding.py` 신규 생성 (383줄)
  - `show_onboarding()`: 3단계 온보딩 플로우 (환영 → 학습 흐름 안내 → 준비 완료)
  - "건너뛰기" 버튼 항상 표시, 완료 시 session_state["onboarding_done"] = True

- `ui/components.py` 신규 생성 (773줄)
  - `render_code_editor()`: 데스크탑(streamlit-code-editor) / 모바일(st.text_area) 분기, session_state 기반 코드 유지
  - `render_execution_result()`: 에러 타입별 친절한 안내 (SyntaxError/IndentationError/NameError 체크리스트)
  - `render_grade_result()`: 통과/부분통과/실패 3단계 디자인
  - `render_progress_bar()`: 퍼센트 레이블 + st.progress 조합
  - `render_hint_panel()`: 보상 프레이밍(+20% 보너스), 3단계 힌트, 정답보기/건너뛰기 탈출구
  - `render_problem_navigation()`: 완료 체크마크 + 난이도 아이콘 표시
  - `render_concept_card()`: 마크다운 + 코드 예제 카드
  - `render_difficulty_badge()`: 색상+텍스트+아이콘 3채널 접근성

- `ui/chapter_renderer.py` 신규 생성 (423줄)
  - `ChapterRenderer` 클래스: 탭(개념학습/실습문제/퀴즈) 기반 렌더링
  - 진행도 가중치: 개념 20% + 실습 60% + 퀴즈 20%
  - ProblemRenderer/QuizRenderer에 위임, utils 미구현 시 graceful degradation

- `ui/problem_renderer.py` 신규 생성 (554줄)
  - `ProblemRenderer` 클래스: 난이도 필터 체크박스, 좌우 분할 문제 네비게이션
  - 실행/제출/초기화 버튼 분리, 힌트 사용 횟수 기반 보너스 계산
  - 힌트 보너스: 0개→+20%, 1개→+13%, 2개→+6%, 3개→0%

- `ui/quiz_renderer.py` 신규 생성 (536줄)
  - `QuizRenderer` 클래스: multiple_choice(radio)/ox(radio 수평)/fill_blank(text_input)
  - 즉시 채점 + 정답/해설 표시 + 재응시 옵션
  - fill_blank: strip().lower() 대소문자 무시 채점

### 설계 결정
- 모든 외부 의존성(core/executor, core/grader, utils)은 try/except ImportError로 graceful degradation 처리
- 에러 디자인: 빨간색 대신 노란-주황 계열(#FFFBEB)로 초보자 불안 최소화
- 접근성: 난이도 배지는 색상+텍스트+아이콘 3채널 병용 (색맹 사용자 고려)
- 모바일 분기: session_state["use_mobile_editor"] 토글 버튼 방식

### 개선점
- 이전 대비: UI 모듈 전무 → 6개 파일 완전 구현
- 총 3,197줄 한국어 docstring + 인라인 주석 포함

---

## 2026-03-07: 코어 보안/실행 엔진 모듈 구현

### 변경 내용
- `core/security.py` 신규 생성: AST 기반 2단계 보안 검증기
- `core/executor.py` 신규 생성: subprocess 격리 코드 실행 엔진
- `core/error_translator.py` 신규 생성: Python 에러 한국어 번역
- `core/utils.py` 신규 생성: JSON 로드, 출력 정규화 등 유틸리티
- `core/__init__.py` 업데이트: 전체 모듈 re-export

### 구현 세부 사항

#### core/security.py
- `SecurityValidator(ast.NodeVisitor)`: dunder 속성/이름 차단, 챕터별 import 제어, 위험 함수 호출 차단
  - BLOCKED_ATTRIBUTES: 10종 (__subclasses__, __bases__, __mro__, __globals__ 등)
  - ALLOWED_DUNDERS: 5종 (__init__, __str__, __repr__, __len__, __name__)
  - BLOCKED_FUNCTIONS: 12종 (exec, eval, compile, open, globals, locals 등)
  - 기본 허용 모듈 8종 + Ch8 추가 2종(numpy, pandas) + 항상 차단 15종
- `MemorySafetyValidator(ast.NodeVisitor)`: 리소스 남용 사전 차단
  - 거대 상수(>10^6), 거대 range(), 문자열 곱셈 차단

#### core/executor.py
- `ExecutionResult` dataclass: stdout, stderr, variables, success, error_type, error_line, execution_time
- `CodeExecutor` 클래스: 5단계 실행 파이프라인
  - AST 보안 검증 → 실행 스크립트 생성 → 임시 파일 → subprocess.run → 결과 파싱
  - input() 오버라이드: preset_inputs 순차 제공
  - builtins 스코프 격리: 사용자 코드 네임스페이스에서만 위험 함수 차단
  - safe_import: import depth 추적으로 허용 모듈의 transitive import 허용
  - 변수 추출: base64 인코딩 + JSON 마커 방식
  - 동시 실행 제한: Semaphore(3)
- `VirtualFileSystem` 클래스: Ch6 파일 입출력 학습용 메모리 기반 가상 FS
  - open(r/w/a), with문, close 시 자동 저장

#### core/error_translator.py
- `ErrorTranslator` 클래스: 10종 에러 한국어 번역
  - SyntaxError, NameError, TypeError, IndexError, KeyError, ValueError,
    IndentationError, ZeroDivisionError, AttributeError, FileNotFoundError
- 전각 문자 감지 (18종 매핑: ：→:, ＝→= 등)
- Print → print 대소문자 오류 감지
- 탭/스페이스 혼용 감지
- `sanitize_traceback()`: 서버 경로 마스킹

#### core/utils.py
- `load_json()`, `load_chapter_data()`, `load_problems()`, `load_quiz()`
- `normalize_output()`: trailing whitespace 제거, 연속 빈줄 축소
- `truncate_output()`: 최대 길이 초과 시 줄 단위 절단 + 안내 메시지
- `get_data_dir()`: 프로젝트 data 디렉토리 경로

### 설계 결정
- **보안 계층 분리**: AST 정적 분석(1차) + 런타임 builtins 스코프 격리(2차) + subprocess 프로세스 격리(3차)
- **builtins 오버라이드 최소화**: type/locals/globals/exec 등은 builtins 수준에서 차단하지 않음
  - Python import 시스템(enum.py 등)이 type() 3인자 호출에 의존
  - import 구문이 내부적으로 locals()를 호출
  - numpy 등 내부 모듈이 exec/compile 사용
  - 대신 사용자 코드 exec() globals 딕셔너리에서만 차단
- **import depth 추적**: safe_import에서 depth > 0이면 transitive import 허용
- **base64 코드 전달**: 사용자 코드를 base64로 인코딩하여 문자열 이스케이프 문제 완전 회피

### 개선점
- 이전 대비: 코어 실행 엔진 부재 → 4개 파일 완전 구현
- 15/15 통합 테스트 통과 (기본 실행, 변수 추출, input, 에러, 보안, 모듈, inject, timeout, 메모리, numpy)

---

## 2026-03-07: 챕터 5~8 데이터 JSON + app.py + pages 생성

### 변경 내용

#### 데이터 JSON (12개 파일)

**챕터 5 - 함수와 클래스**
- `data/chapters/chapter5.json`: 5개 섹션 (함수 정의, 매개변수, 변수 범위, 클래스 기초, 상속)
- `data/problems/chapter5_problems.json`: 15개 문제 (기초5+중급5+심화5), 채점 방식: function_exists/function_call/class_check/exact_output
- `data/quizzes/chapter5_quiz.json`: 10개 퀴즈 (multiple_choice/ox/fill_blank)

**챕터 6 - 파일 다루기**
- `data/chapters/chapter6.json`: 4개 섹션 (파일 쓰기, 읽기, with문, 파일 모드)
- `data/problems/chapter6_problems.json`: 15개 문제, `use_virtual_fs: true` + `preset_files` 설정
- `data/quizzes/chapter6_quiz.json`: 10개 퀴즈

**챕터 7 - 예외 처리**
- `data/chapters/chapter7.json`: 4개 섹션 (try/except, 여러 예외, else/finally, raise/사용자정의)
- `data/problems/chapter7_problems.json`: 15개 문제, 예외 처리 패턴 전반
- `data/quizzes/chapter7_quiz.json`: 10개 퀴즈

**챕터 8 - NumPy/Pandas**
- `data/chapters/chapter8.json`: 4개 섹션 (NumPy 배열 생성, 연산, Pandas Series, DataFrame)
- `data/problems/chapter8_problems.json`: 15개 문제, `allowed_modules: ["numpy", "pandas"]` 명시
- `data/quizzes/chapter8_quiz.json`: 10개 퀴즈

#### 코어 모듈 (신규)

- `core/progress.py`: 진행도 관리 (JSON 파일 기반 영속화, 스트릭 계산, 내보내기/가져오기)
- `core/executor.py`: subprocess 격리 실행 + VirtualFileSystem (챕터 6 open() 패치)
- `core/utils.py`: JSON 로드, 경로 관리, 출력 정규화/절단

#### UI 모듈 (신규/보완)

- `ui/onboarding.py`: 초보자 환영 온보딩 (사이드바 방식)
- `ui/components.py`: 재사용 컴포넌트 (진행도 바, 카드, 배지, 채점 결과, 코드 에디터, 네비게이션)
  - 기존 problem_renderer.py가 요구하는 render_code_editor, render_execution_result, render_problem_navigation 함수 추가
- `ui/chapter_renderer.py`: ChapterRenderer 클래스 (개념/문제/퀴즈 탭 통합)

#### 앱 진입점 + pages

- `app.py`: 메인 대시보드 (전체 진행도, 챕터 카드 그리드 4×2, 진행도 내보내기/가져오기)
- `pages/5_📖_챕터5_함수클래스.py`: 챕터 5 학습 페이지
- `pages/6_📖_챕터6_파일다루기.py`: 챕터 6 학습 페이지
- `pages/7_📖_챕터7_예외처리.py`: 챕터 7 학습 페이지
- `pages/8_📖_챕터8_라이브러리.py`: 챕터 8 학습 페이지
- `pages/9_📊_진행현황.py`: 전체 진행현황 대시보드 (챕터별 상세, 난이도별 현황, 학습 이력)

### 설계 결정

- 챕터 6 파일 문제: `open()` builtins 패치 방식으로 가상 파일시스템 구현 (실제 OS 파일시스템 접근 없음)
- chapters 8 모듈: SecurityValidator의 CH8_EXTRA_MODULES 허용 목록(numpy, pandas)과 연동
- 힌트 배율: 0개→1.2, 1개→1.0, 2개→0.9, 3개→0.7 (기존 hint_system.py와 동일)
- 진행도 저장: data/progress.json (JSON 파일, session_state 대신 파일 기반 영속화)

### 개선점
- 이전 대비: 챕터 5~8 학습 콘텐츠 + 페이지 없음 → 완전 구현
- 총 12개 JSON 파일 (챕터당 3개 × 4챕터), 60개 문제, 40개 퀴즈
- 가상 파일시스템으로 챕터 6 브라우저 환경에서 실제 파일 조작 학습 가능
