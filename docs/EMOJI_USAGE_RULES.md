# 이모지 사용 규칙

**Status**: VERIFIED (2025-10-28 테스트 완료)
**Risk Level**: HIGH (Windows cp949 인코딩 오류)
**Occurrences**: 8회 반복

---

## 핵심 규칙 (절대 규칙)

### ❌ 절대 금지
```python
# Python 코드 (.py 파일)
print("✅ Complete")  # [ERROR] cp949 error
print(history_section)  # [ERROR] if content has emoji
logger.info("📝 Update")  # [ERROR] console output
```

### ✅ 허용
```markdown
<!-- Markdown 파일 (.md) -->
## 📝 Update History
- ✅ 완료
- ❌ 실패
```

```json
{
  "title": "📝 Document"  // JSON with UTF-8 encoding
}
```

---

## 파일 타입별 규칙

| 파일 타입 | 이모지 허용 | 이유 |
|----------|-----------|------|
| **.py** | ❌ 절대 금지 | Windows cp949 console encoding |
| **.md** | ✅ 허용 | UTF-8 지원, 가독성 향상 |
| **.json** | ✅ 조건부 | `ensure_ascii=False` 필요 |
| **Obsidian** | ✅ 허용 | 문서 품질 개선 |

---

## 검증된 위험 패턴

### 패턴 1: print() with emoji
```python
# [HIGH RISK]
print(f"Status: {status_emoji}")

# [SAFE]
print(f"Status: [OK]")
```

### 패턴 2: 파일 내용 출력
```python
# [HIGH RISK]
content = file.read_text()  # contains emoji
print(content)  # [ERROR]

# [SAFE]
content = file.read_text()
# Use Read tool to display instead of print()
```

### 패턴 3: Logger with emoji
```python
# [HIGH RISK]
logger.info("✅ Task completed")

# [SAFE]
logger.info("[OK] Task completed")
```

---

## ASCII 대체 문자

| 이모지 | ASCII | 용도 |
|-------|-------|------|
| ✅ | `[OK]` | 성공 |
| ❌ | `[X]` | 실패 |
| ⚠️ | `[!]` | 경고 |
| 📝 | `[NOTE]` | 메모 |
| 🚀 | `[>>]` | 진행 |
| 📊 | `[STATS]` | 통계 |

---

## 자동 검증

### Pre-Execution Guard
```bash
python scripts/pre_execution_guard.py your_script.py
```

검증 항목:
1. `print()` with emoji detection
2. File content printing detection
3. Logger with emoji detection

---

## 오류 발생 시 대응

### 증상
```
UnicodeEncodeError: 'cp949' codec can't encode character '\U0001f4dd'
```

### 원인
Windows 콘솔이 cp949 인코딩 사용, 이모지 불가

### 해결
1. Python 코드에서 이모지 제거
2. ASCII 대체 문자 사용 ([OK], [X])
3. 또는 파일에만 쓰고 Read 도구로 표시

---

## 실수 방지 체크리스트

코드 작성 전:
- [ ] Python 파일인가? → 이모지 사용하지 않기
- [ ] print() 사용하는가? → 내용에 이모지 없는지 확인
- [ ] 파일 내용 출력하는가? → Read tool 사용하기

코드 실행 전:
- [ ] `python scripts/pre_execution_guard.py` 실행
- [ ] 위반 사항 없는지 확인

---

## 참고 문서

- `RUNS/error_learning_db.json` - 에러 E001, E002, E003
- `scripts/pre_execution_guard.py` - 자동 검증 도구
- `docs/EMOJI_COMPLETE_ANALYSIS.md` - 완전 분석 보고서

---

**Last Updated**: 2025-10-29
**Verified By**: 실제 테스트 (8회 오류 경험)
**Status**: ACTIVE - 모든 코드 작성 시 준수 필수
