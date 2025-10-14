# 프로젝트 빠른 시작 가이드 (Quick Start Guide)

## 🎯 프로젝트 목표
도서 텍스트를 비디오 스크립트 형식으로 변환하는 LLM 모델 개발

## 📅 이번 주 마감 (10월 27일)
데이터 수집 및 전처리 완료

## 🚀 빠른 시작

### 1. 환경 설정 (5분)
```bash
# 필수 라이브러리 설치
pip install torch transformers datasets nltk spacy beautifulsoup4 requests scikit-learn

# SpaCy 모델 다운로드
python -m spacy download en_core_web_sm

# NLTK 데이터 다운로드 (Python에서)
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"
```

### 2. 데이터 수집 시작 (10분)
```python
# data_preprocessing.ipynb 열기
# 아래 셀 실행:

from data_preprocessing import *

# 1. 수집기 초기화
collector = GutenbergCollector()

# 2. 샘플 도서 다운로드
book_id = 1342  # Pride and Prejudice
book_text = collector.download_book(book_id)

# 3. 결과 확인
print(f"Downloaded {len(book_text)} characters")
```

### 3. 전처리 실행 (20분)
```python
# 전체 파이프라인 실행
pipeline = BookToScriptPipeline()

# 샘플 도서 처리
result = pipeline.process_book(1342)

# 결과 확인
print(f"Processed {result['total_chapters']} chapters")
```

## 📊 역할 분담 (교수님 지시사항)

### 👤 역할 A: 데이터 수집 집중
**시간 배분**: 60%

**이번 주 목표**:
- [ ] 50권 이상 도서 수집
- [ ] 다양한 장르 확보

**매일 할 일**:
```python
# 매일 10-15권씩 다운로드
book_ids = collector.get_popular_books(limit=15)
for book_id in book_ids:
    text = collector.download_book(book_id)
    # 저장
```

### 👥 역할 B: 프레임워크 셋업
**시간 배분**: 40%

**이번 주 목표**:
- [ ] 전처리 파이프라인 최적화
- [ ] 데이터 품질 검증
- [ ] 모델 조사

**매일 할 일**:
- 전처리 코드 개선
- 샘플 데이터 테스트
- LLM 모델 문서 읽기

## 📝 일일 체크리스트

### 월요일
- [ ] 환경 설정 완료
- [ ] 샘플 데이터 테스트
- [ ] 도서 10권 수집

### 화요일
- [ ] 도서 15권 수집
- [ ] 전처리 파이프라인 검증
- [ ] 팀 회의 (진행 상황 공유)

### 수요일
- [ ] 도서 15권 수집
- [ ] 데이터 품질 검증 시작
- [ ] 문제점 기록

### 목요일
- [ ] 도서 10권 수집
- [ ] 데이터 통계 분석
- [ ] 팀 회의 (중간 점검)

### 금요일
- [ ] 전체 데이터 전처리 실행
- [ ] 결과 확인 및 정리
- [ ] 학습 데이터 포맷 정의

### 주말
- [ ] 보고서 작성
- [ ] 다음 주 계획 수립
- [ ] 발표 자료 준비

## 🔧 주요 코드 스니펫

### 도서 대량 다운로드
```python
# 50권 다운로드
collector = GutenbergCollector()
book_ids = collector.get_popular_books(limit=50)

for i, book_id in enumerate(book_ids, 1):
    print(f"[{i}/50] Downloading book {book_id}...")
    text = collector.download_book(book_id)
    if text:
        with open(f'raw_data/book_{book_id}.txt', 'w') as f:
            f.write(text)
```

### 전체 파이프라인 실행
```python
# 모든 수집된 도서 처리
pipeline = BookToScriptPipeline()
results = pipeline.process_multiple_books(
    book_ids,
    output_dir='./processed_data'
)
```

### 데이터 통계 확인
```python
# 통계 계산
total_books = len(results)
total_chapters = sum(r['total_chapters'] for r in results)
total_chars = sum(r['total_length'] for r in results)

print(f"📚 Total Books: {total_books}")
print(f"📖 Total Chapters: {total_chapters}")
print(f"📝 Total Characters: {total_chars:,}")
```

## 📌 중요 파일

### 작업 파일
- `data_preprocessing.ipynb` - 메인 작업 노트북
- `processed_data/` - 처리된 데이터 저장
- `raw_data/` - 원본 데이터 저장

### 문서
- `README.md` - 프로젝트 개요
- `DATA_PREPROCESSING_GUIDE.md` - 상세 가이드
- `QUICK_START.md` - 이 파일

## ⚠️ 주의사항

### 데이터 수집
- ✅ Project Gutenberg는 로봇 접근 제한이 있으니 적절한 딜레이 설정
- ✅ 다운로드 실패 시 재시도 로직 구현
- ✅ 저장 공간 확인 (50권 ≈ 50-100MB)

### 전처리
- ✅ 메모리 부족 시 배치 처리
- ✅ 챕터 분할 실패 시 수동 확인
- ✅ 정기적으로 중간 결과 저장

### 협업
- ✅ 매일 오후 6시 진행 상황 공유
- ✅ 문제 발생 시 즉시 공유
- ✅ 코드 변경 시 커밋 메시지 명확히

## 🆘 문제 해결

### "메모리 부족" 에러
```python
# 텍스트 길이 제한
max_length = 100000  # 10만 자로 제한
doc = nlp(text[:max_length])
```

### "다운로드 실패" 에러
```python
# 재시도 로직
import time
for retry in range(3):
    text = collector.download_book(book_id)
    if text:
        break
    time.sleep(5)  # 5초 대기 후 재시도
```

### "챕터 분할 실패"
```python
# 다양한 패턴 시도
chapters = preprocessor.split_into_chapters(text)
if len(chapters) == 1:
    # 수동 확인 필요
    print(f"⚠️ Book {book_id}: Chapter split failed")
```

## 📞 연락처

- 팀 채팅: [팀 채팅방 링크]
- 정기 회의: 화요일, 목요일 오후 7시
- 긴급 연락: [연락처]

## ✅ 완료 기준

### 데이터 수집 (10월 27일까지)
- [ ] 50권 이상 도서 수집 완료
- [ ] 다양한 장르 확보 (소설 60%, 드라마 20%, 미스터리 20%)
- [ ] 원본 데이터 백업 완료

### 데이터 전처리
- [ ] 모든 도서 전처리 완료
- [ ] 데이터 품질 검증 완료
- [ ] 결측치/이상치 처리 완료

### 문서화
- [ ] 진행 상황 보고서 작성
- [ ] 데이터 통계 정리
- [ ] 다음 단계 계획 수립

---

**시작일**: 2025년 10월 12일  
**마감일**: 2025년 10월 27일  
**다음 단계**: 모델링 (10월 28일~)

💪 **화이팅!**
