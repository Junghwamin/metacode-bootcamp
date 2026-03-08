"""AI 튜터 챗봇 모듈.

OpenAI GPT API를 사용하여 학습자에게 맞춤형 교육 지원을 제공한다.
정답을 직접 알려주지 않고, 힌트와 설명 위주로 가르치는 교육용 챗봇.

시스템 프롬프트로 역할을 제한하고, 현재 챕터/문제 컨텍스트를
자동 주입하여 맥락에 맞는 답변을 생성한다.

Note:
    - API 키는 Streamlit secrets에서 로드 (st.secrets["OPENAI_API_KEY"])
    - 모델: gpt-4o-mini (비용 효율적, 교육용 Q&A에 충분)
    - 응답 max_tokens=500 (장문 방지)
    - 대화 기록: 최근 10턴만 유지 (토큰 절약)
"""

from openai import OpenAI

# === 시스템 프롬프트 ===
# 교육자 역할을 명확히 정의하고, 정답 코드 직접 제공을 금지한다.
SYSTEM_PROMPT = """당신은 '메타코드 파이썬 튜터'입니다. Python을 처음 배우는 한국어 사용자를 돕습니다.

## 핵심 규칙
1. **절대로 정답 코드를 직접 제공하지 마세요.** 대신 힌트, 개념 설명, 디버깅 가이드를 제공하세요.
2. 초보자 눈높이에 맞춰 쉬운 용어로 설명하세요.
3. 틀린 부분이 있으면 왜 틀렸는지 원인을 설명하고, 올바른 방향을 힌트로 알려주세요.
4. 코드 조각(snippet)은 3줄 이내로만 보여주세요. 전체 솔루션은 절대 안 됩니다.
5. 격려와 칭찬을 적극 사용하세요.

## 답변 구조 (반드시 What → Why → How 순서로)
모든 답변은 아래 3단계 구조를 따르세요:

**What** (1~2문장): 질문한 개념이 무엇인지 한 줄로 정의합니다. 비유를 활용하세요.
**Why** (1~2문장): 왜 이것이 중요한지, 실제로 어디서 쓰이는지 동기를 부여합니다.
**How** (2~3문장): 어떻게 사용하는지 힌트나 방향을 제시합니다. 코드 조각은 3줄 이내.

예시:
Q: "변수가 뭐에요?"
A:
🔍 **What**: 변수는 데이터를 담아두는 이름표예요. `name = '홍길동'`처럼 쓰면 '홍길동'이라는 값에 name이라는 이름을 붙이는 거죠.

💡 **Why**: 같은 값을 여러 번 쓸 때 매번 직접 입력하면 실수하기 쉬워요. 변수에 한 번 저장하면 이름만으로 꺼내 쓸 수 있답니다.

🛠 **How**: `=` 기호 왼쪽에 이름, 오른쪽에 값을 넣으세요. 이름은 영문자로 시작하고, 의미 있는 이름을 쓰면 나중에 읽기 편해요!

## 할 수 있는 것
- 개념 설명 (변수, 반복문, 함수 등)
- 에러 메시지 해석 및 해결 방향 안내
- 코드 리뷰 (개선점 피드백)
- 문제 풀이 힌트 제공

## 할 수 없는 것
- 정답 코드 전체 제공
- 과제/시험 대리 풀이
- Python과 무관한 질문 응답
"""


def get_context_prompt(chapter_id: int = None, problem_title: str = None,
                       user_code: str = None, error_msg: str = None) -> str:
    """현재 학습 컨텍스트를 시스템 프롬프트에 추가한다.

    챕터, 문제, 사용자 코드, 에러 메시지 등을 자동 주입하여
    맥락에 맞는 답변을 생성할 수 있게 한다.

    Args:
        chapter_id: 현재 챕터 번호 (1~8)
        problem_title: 현재 풀고 있는 문제 제목
        user_code: 사용자가 작성한 코드
        error_msg: 발생한 에러 메시지

    Returns:
        컨텍스트가 포함된 추가 시스템 프롬프트 문자열
    """
    chapter_topics = {
        1: "Python 기초 (print, input, 변수, 주석)",
        2: "데이터 타입 (int, float, str, bool)",
        3: "자료형 (list, tuple, set, dict)",
        4: "조건문과 반복문 (if, for, while)",
        5: "함수와 클래스 (def, class, 상속)",
        6: "파일 다루기 (open, read, write)",
        7: "예외 처리 (try, except, finally)",
        8: "라이브러리 (NumPy, Pandas)",
        9: "통계의 기초와 데이터 (평균, 분산, 상관계수, 기술통계)",
        10: "확률과 확률변수 (확률, 조건부확률, 베이즈정리, 기대값)",
        11: "확률분포 (이항분포, 정규분포, CLT, t분포)",
        12: "통계적 추정과 검정 (신뢰구간, 가설검정, p-value)",
        13: "두 모집단 비교와 분산분석 (t검정, ANOVA)",
        14: "회귀분석 (최소제곱법, R², 잔차분석)",
        15: "Pandas 데이터 분석 (DataFrame, groupby, merge, pivot)",
        16: "데이터 시각화 with Plotly (bar, line, histogram, scatter)",
        17: "마케팅 데이터 분석 (기여분석, 전환윈도우, ROAS, CPC)",
    }

    parts = []
    if chapter_id and chapter_id in chapter_topics:
        parts.append(f"현재 학습 중인 챕터: {chapter_id}장 - {chapter_topics[chapter_id]}")
    if problem_title:
        parts.append(f"현재 문제: {problem_title}")
    if user_code:
        parts.append(f"학습자의 코드:\n```python\n{user_code[:500]}\n```")
    if error_msg:
        parts.append(f"발생한 에러:\n```\n{error_msg[:300]}\n```")

    if parts:
        return "\n\n## 현재 학습 컨텍스트\n" + "\n".join(parts)
    return ""


def chat_with_tutor(messages: list, api_key: str,
                    chapter_id: int = None, problem_title: str = None,
                    user_code: str = None, error_msg: str = None) -> str:
    """GPT API를 호출하여 튜터 응답을 생성한다.

    Args:
        messages: 대화 기록 리스트 [{"role": "user"/"assistant", "content": str}, ...]
        api_key: OpenAI API 키
        chapter_id: 현재 챕터 번호
        problem_title: 현재 문제 제목
        user_code: 사용자 코드 (에러 질문 시)
        error_msg: 에러 메시지 (에러 질문 시)

    Returns:
        튜터의 응답 문자열

    Raises:
        Exception: API 호출 실패 시
    """
    client = OpenAI(api_key=api_key)

    # 시스템 프롬프트 + 컨텍스트 조합
    context = get_context_prompt(chapter_id, problem_title, user_code, error_msg)
    system_msg = SYSTEM_PROMPT + context

    # 최근 10턴만 유지 (토큰 절약)
    recent_messages = messages[-20:]  # user+assistant 쌍이므로 10턴 = 20개

    api_messages = [{"role": "system", "content": system_msg}] + recent_messages

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=api_messages,
        max_tokens=500,
        temperature=0.7,
    )

    return response.choices[0].message.content
