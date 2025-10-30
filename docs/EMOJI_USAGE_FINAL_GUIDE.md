# Final Emoji Usage Guide
## 테스트 기반 최종 가이드라인

**Date**: 2025-10-28
**Based on**: 실제 테스트 결과

---

## [TESTED] 실제 테스트 결과

### 안전한 영역 (이모지 사용 가능)
1. **옵시디언 .md 파일** - [OK] 읽기/쓰기 모두 정상
2. **JSON 파일** - [OK] ensure_ascii=False + UTF-8
3. **변수 내부 처리** - [OK] 메모리에서는 안전
4. **HTML/Web** - [OK] 브라우저가 UTF-8 처리

### 위험한 영역 (이모지 절대 금지)
1. **Python print()** - [ERROR] Windows 콘솔 출력 실패
2. **logger.info()** - [ERROR] 로그 출력 실패
3. **encoding 미지정** - [ERROR] cp949로 읽기 실패

---

## 권장 방식

### 방식 1: 이중 처리 (Best Practice)
```python
class SafeObsidianBridge:
    def save_to_obsidian(self, data):
        # 옵시디언용 (이모지 포함)
        obsidian_content = f"## 상태: ✅ 완료\n작업: 🎯 목표 달성"
        with open("note.md", "w", encoding="utf-8") as f:
            f.write(obsidian_content)  # OK

        # 콘솔 출력용 (ASCII 변환)
        console_content = obsidian_content.replace("✅", "[OK]").replace("🎯", "[TARGET]")
        print(console_content)  # Safe
```

### 방식 2: 조건부 처리
```python
def smart_output(content, to_file=False, to_console=False):
    if to_file:
        # 파일에는 이모지 그대로
        with open("output.md", "w", encoding="utf-8") as f:
            f.write(content)  # 이모지 OK

    if to_console:
        # 콘솔에는 ASCII 변환
        ascii_content = convert_to_ascii(content)
        print(ascii_content)  # Safe
```

### 방식 3: 별도 매핑 관리
```python
EMOJI_MAP = {
    # 옵시디언용 -> 콘솔용
    "✅": "[OK]",
    "❌": "[X]",
    "⚠️": "[!]",
    "🎯": "[>>]",
    "🚀": "[GO]",
    "💡": "[*]"
}

def safe_print(text):
    for emoji, ascii_ver in EMOJI_MAP.items():
        text = text.replace(emoji, ascii_ver)
    print(text)
```

---

## 프로젝트별 권장사항

### 우리 프로젝트 (Dev Rules)
```yaml
file_types:
  "*.py":
    emojis: NO      # Python 코드 - 금지
    reason: "콘솔 출력 에러"

  "*.md":
    emojis: YES     # 문서 - 허용
    reason: "UTF-8로 안전"

  "RUNS/**":
    emojis: NO      # 증거 파일 - 금지
    reason: "콘솔에서 읽을 가능성"

  "obsidian/**":
    emojis: YES     # 옵시디언 - 허용
    reason: "옵시디언 전용"
```

---

## 실용적 가이드

### DO (하세요)
- [O] 옵시디언 메모에 이모지 사용
- [O] UTF-8 encoding 항상 명시
- [O] 파일 저장 시 이모지 포함 가능
- [O] 웹/HTML에 이모지 사용

### DON'T (하지 마세요)
- [X] Python print()에 이모지
- [X] 로거 출력에 이모지
- [X] encoding 없이 파일 읽기
- [X] 콘솔 출력용 텍스트에 이모지

### CONVERT (변환하세요)
```python
# 파일에서 읽은 후 콘솔 출력 시
content = file.read_text(encoding="utf-8")  # 이모지 포함
if need_console_output:
    content = convert_emojis_to_ascii(content)
    print(content)  # 이제 안전
```

---

## 결론

**"파일에는 이모지 OK, 콘솔에는 이모지 NO"**

이것이 가장 실용적이고 안전한 접근법입니다.

### 최종 체크리스트
- [ ] Python 파일: 이모지 제거했나?
- [ ] 콘솔 출력: ASCII로 변환했나?
- [ ] 파일 읽기: UTF-8 명시했나?
- [ ] 옵시디언: 이모지 자유롭게 사용 중?

이 가이드를 따르면 인코딩 에러 없이 안전하게 개발할 수 있습니다!
