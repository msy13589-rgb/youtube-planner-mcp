"""
YouTube Planner(유튜브 기획 비서) MCP 서버
카카오 PlayMCP / AGENTIC PLAYER 10 출품작.

PlayMCP 개발가이드 준수:
- Streamable HTTP(루트 경로), Stateless(no session)
- 각 tool에 annotations 지정
"""

from __future__ import annotations
import os
import re
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

mcp = FastMCP("youtube-planner", stateless_http=True)

POWER_WORDS = [
              "충격", "진짜", "실화", "완벽", "총정리", "꿀팁", "비법", "이유", "방법",
              "후기", "비교", "무료", "최초", "최고", "솔직", "폭로", "반전", "레전드",
              "역대급", "미쳤다", "대박", "필수", "주의", "손해", "결국", "드디어",
]
CURIOSITY_WORDS = ["왜", "어떻게", "만약", "과연", "진짜", "이것", "이거", "그", "숨겨진"]


def _keyword(topic: str) -> str:
              tokens = re.sub(r"[^\w가-힣 ]", " ", topic).split()
              return tokens[-1] if tokens else topic.strip()


def generate_video_plan(topic: str, audience: str = "일반 시청자", tone: str = "친근함") -> dict:
              topic = topic.strip()
              kw = _keyword(topic)
              titles = [
                  f"{topic}, 이것만 알면 끝나요",
                  f"아무도 안 알려주는 {kw} 꿀팁 5가지",
                  f"{topic} 직접 해봤습니다 (솔직 후기)",
                  f"3분 만에 끝내는 {topic}",
                  f"{kw} 이렇게 하면 100% 후회합니다",
              ]
              thumbnails = [f"{kw} 총정리", "이거 모르면 손해", f"{kw}, 진짜 이게 맞아?"]
              script = {
                  "훅": f"'{kw}, 아직도 모르세요?' 시청자 문제를 한 문장으로 던져 이탈을 막는다.",
                  "본론1": f"{kw}의 핵심 개념을 쉽게 설명한다.",
                  "본론2": f"예시와 비교로 {kw}를 눈으로 보여준다.",
                  "본론3": "자주 하는 실수와 꿀팁을 정리한다.",
                  "마무리": "3줄 요약과 다음 영상 예고, 구독 유도.",
              }
              tags = list(dict.fromkeys(
                  [kw, topic.replace(" ", "")]
                  + re.sub(r"[^\w가-힣 ]", " ", topic).split()
                  + ["유튜브", "브이로그", "꿀팁", "정보"]
              ))
              hashtags = ["#" + t for t in tags if t][:10]
              return {
                  "주제": topic,
                  "타겟": audience,
                  "톤": tone,
                  "제목_후보": titles[:3],
                  "제목_예비안": titles[3:],
                  "썸네일_문구": thumbnails,
                  "대본_구조": script,
                  "해시태그": hashtags,
              }


def evaluate_thumbnail(title: str, thumbnail_text: str = "") -> dict:
              title = title.strip()
              combined = f"{title} {thumbnail_text}".strip()
              length = len(title.replace(" ", ""))
              breakdown, suggestions, score = {}, [], 0
              if 12 <= length <= 26:
                                breakdown["길이"] = 25
elif length < 12:
        breakdown["길이"] = 12
        suggestions.append("제목이 짧아요. 12자 이상으로 늘려보세요.")
else:
        breakdown["길이"] = 12
                  suggestions.append("제목이 길어요. 26자 이내로 줄여보세요.")
    score += breakdown["길이"]
    if re.search(r"\d", combined):
                      breakdown["숫자"] = 20
else:
        breakdown["숫자"] = 0
        suggestions.append("숫자를 넣으면 클릭률이 올라가요.")
    score += breakdown["숫자"]
    hit_power = [w for w in POWER_WORDS if w in combined]
    breakdown["파워워드"] = min(len(hit_power) * 12, 25)
    if not hit_power:
                      suggestions.append("강한 단어를 하나 넣어보세요.")
                  score += breakdown["파워워드"]
    hit_cur = [w for w in CURIOSITY_WORDS if w in combined]
    breakdown["호기심"] = 15 if hit_cur else 0
    if not hit_cur:
                      suggestions.append("호기심 표현으로 궁금하게 만드세요.")
                  score += breakdown["호기심"]
    if thumbnail_text and len(thumbnail_text.replace(" ", "")) <= 12:
                      breakdown["썸네일"] = 15
elif thumbnail_text:
        breakdown["썸네일"] = 7
        suggestions.append("썸네일 문구는 6~8자로 짧게.")
else:
        breakdown["썸네일"] = 0
        suggestions.append("썸네일 문구도 정해보세요.")
    score += breakdown["썸네일"]
    score = min(score, 100)
    grade = "매우 좋음" if score >= 80 else "괜찮음" if score >= 60 else "개선 필요"
    return {
                      "제목": title,
                      "썸네일_문구": thumbnail_text or "(없음)",
                      "클릭률_점수": score,
                      "등급": grade,
                      "항목별_점수": breakdown,
                      "개선_제안": suggestions or ["훌륭해요!"],
    }


@mcp.tool(
              annotations=ToolAnnotations(
                                title="영상 기획 생성 (Video Plan)",
                                readOnlyHint=True,
                                destructiveHint=False,
                                idempotentHint=True,
                                openWorldHint=False,
              )
)
def plan_video(topic: str, audience: str = "일반 시청자", tone: str = "친근함") -> dict:
              """Generate YouTube video title ideas, thumbnail copy, a script outline, and hashtags from a topic. Service: YouTube Planner(유튜브 기획 비서)."""
              return generate_video_plan(topic, audience, tone)


@mcp.tool(
              annotations=ToolAnnotations(
                                title="썸네일 클릭률 진단 (Thumbnail CTR Score)",
                                readOnlyHint=True,
                                destructiveHint=False,
                                idempotentHint=True,
                                openWorldHint=False,
              )
)
def score_thumbnail(title: str, thumbnail_text: str = "") -> dict:
              """Score the click-through-rate potential (0-100) of a YouTube title and thumbnail text, and suggest concrete improvements. Service: YouTube Planner(유튜브 기획 비서)."""
              return evaluate_thumbnail(title, thumbnail_text)


if __name__ == "__main__":
              if os.getenv("MCP_HTTP", "1") == "1":
                                mcp.settings.host = os.getenv("HOST", "0.0.0.0")
                                mcp.settings.streamable_http_path = "/"
                                mcp.settings.port = int(os.getenv("PORT", "8080"))
                                mcp.run(transport="streamable-http")
else:
        mcp.run()
