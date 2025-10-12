# 실행 가이드 (Execution Guide)

## 즉시 실행 가능한 완성된 코드

이 가이드는 `data_preprocessing.ipynb` 노트북을 처음부터 끝까지 실행하는 방법을 단계별로 설명합니다.

---

## 목차

1. [환경 설정](#1-환경-설정)
2. [노트북 실행 순서](#2-노트북-실행-순서)
3. [각 셀의 기능](#3-각-셀의-기능)
4. [실행 결과 확인](#4-실행-결과-확인)
5. [문제 해결](#5-문제-해결)

---

## 1. 환경 설정

### 1.1 필수 라이브러리 설치

```bash
# 방법 1: pip를 사용한 설치
pip install torch transformers datasets nltk spacy beautifulsoup4 requests scikit-learn

# 방법 2: requirements.txt 사용 (프로젝트 루트에 파일 생성 후)
pip install -r requirements.txt
```

### 1.2 SpaCy 모델 다운로드

```bash
# 영어 모델
python -m spacy download en_core_web_sm

# 한국어 모델 (선택사항)
python -m spacy download ko_core_news_sm
```

### 1.3 NLTK 데이터 다운로드

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger'); nltk.download('maxent_ne_chunker'); nltk.download('words')"
```

### 1.4 환경 확인

```python
# Python 3.8 이상인지 확인
python --version

# 설치 확인
python -c "import torch, transformers, spacy, nltk; print('✓ All libraries installed')"
```

---

## 2. 노트북 실행 순서

### 2.1 Jupyter 노트북 실행

```bash
# Jupyter Notebook 실행
jupyter notebook data_preprocessing.ipynb

# 또는 JupyterLab
jupyter lab data_preprocessing.ipynb
```

### 2.2 Google Colab 실행

1. Google Colab 접속: https://colab.research.google.com/
2. `File` → `Open notebook` → `GitHub`
3. URL 입력: `https://github.com/dolphin1404/AI_lab`
4. `data_preprocessing.ipynb` 선택

### 2.3 실행 방법

**전체 실행**:
- `Runtime` → `Run all` (Colab)
- `Kernel` → `Restart & Run All` (Jupyter)

**단계별 실행**:
- `Shift + Enter`: 현재 셀 실행 후 다음 셀로 이동
- `Ctrl + Enter`: 현재 셀만 실행

---

## 3. 각 셀의 기능

### Cell 1: Colab 링크 (Markdown)
**기능**: Google Colab에서 열기 링크  
**실행**: 필요 없음

### Cell 2: 프로젝트 개요 (Markdown)
**기능**: 프로젝트 설명  
**실행**: 필요 없음

### Cell 3: 라이브러리 설치
**기능**: 필수 라이브러리 설치  
**예상 시간**: 2-5분  
**출력 예시**:
```
Collecting gutenberg
Collecting requests
...
Successfully installed gutenberg-0.8.2 requests-2.31.0 ...
```

### Cell 4: 라이브러리 임포트
**기능**: 필요한 라이브러리 임포트 및 초기화  
**예상 시간**: 10-30초  
**중요**: 이 셀이 성공해야 다음 셀 실행 가능  
**출력 예시**:
```
[nltk_data] Downloading package punkt to ...
[nltk_data] Downloading package stopwords to ...
✓ All libraries imported successfully!
```

**오류 발생 시**:
```python
# SpaCy 모델 미설치 오류
# 해결: !python -m spacy download en_core_web_sm
```

### Cell 5: GutenbergCollector 클래스
**기능**: Project Gutenberg에서 도서 다운로드  
**예상 시간**: 즉시  
**출력 예시**:
```
✓ Gutenberg Collector initialized
Sample book IDs: [1342, 84, 98, 1661, 2701]
```

**클래스 구조**:
```python
GutenbergCollector
├── download_book(book_id)        # 도서 다운로드
└── get_popular_books(limit=10)   # 인기 도서 ID 반환
```

### Cell 6: 샘플 도서 다운로드
**기능**: Pride and Prejudice (1342) 다운로드  
**예상 시간**: 5-10초 (인터넷 속도에 따라)  
**출력 예시**:
```
✓ Successfully downloaded book 1342
Book length: 717234 characters

First 500 characters:
The Project Gutenberg eBook of Pride and Prejudice...
```

**주의사항**:
- 인터넷 연결 필요
- Project Gutenberg 서버 상태에 따라 실패 가능
- 실패 시 다른 book_id로 재시도

### Cell 7: TextPreprocessor 클래스
**기능**: 텍스트 전처리 및 챕터 분할  
**예상 시간**: 즉시  
**출력 예시**:
```
✓ Text Preprocessor initialized (v2 - improved chapter splitting)
```

**클래스 메서드**:
```python
TextPreprocessor
├── remove_gutenberg_header_footer(text)    # 헤더/푸터 제거
├── remove_table_of_contents(text)          # 목차 제거
├── clean_text(text)                        # 텍스트 정제
├── split_into_chapters(text)               # 챕터 분할
└── _fallback_chapter_split(text)           # Fallback 분석
```

**주요 기능**:
1. **목차 제거**: "Heading to Chapter" 패턴 감지
2. **다중 패턴 매칭**: CHAPTER I, Chapter 1, BOOK I 등
3. **길이 검증**: 평균 500자 이상만 유효 챕터
4. **Fallback**: 줄 단위 분석

### Cell 8: 전처리 적용
**기능**: 다운로드한 도서에 전처리 적용  
**예상 시간**: 1-2초  
**출력 예시**:
```
✓ Original length: 743383 characters
✓ Cleaned length: 720973 characters
✓ Removed: 22410 characters

✓ Found 61 chapters

First chapter: Chapter I
Content preview: It is a truth universally acknowledged, that a single man...
```

**검증 포인트**:
- ✅ Removed characters > 0 (헤더/푸터 제거됨)
- ✅ Chapters > 1 (챕터 분할 성공)
- ✅ 첫 챕터 제목이 "Full Text"가 아님

### Cell 9: 챕터 분할 디버깅
**기능**: 챕터 분할 과정 상세 분석  
**예상 시간**: 2-3초  
**출력 예시**:
```
=== 챕터 분할 디버깅 ===

1. 원본 텍스트 샘플 (처음 1000자):
...

2. 챕터 패턴 검색 결과:
  - CHAPTER/Chapter + 번호: 61개 발견
  - 로마자/숫자만: 15개 발견

3. 챕터 분할 결과:
  총 61개 챕터 발견

  Chapter 1:
    제목: 'Chapter I'
    길이: 11523 문자
    내용 미리보기: It is a truth universally...

4. 챕터 길이 통계:
  - 평균: 11819 문자
  - 최소: 5234 문자
  - 최대: 18976 문자
```

### Cell 10: EntityExtractor 클래스
**기능**: 개체명 추출 (NER)  
**예상 시간**: 즉시  
**출력 예시**:
```
✓ Entity Extractor initialized
```

**클래스 메서드**:
```python
EntityExtractor
├── extract_entities(text)          # 모든 개체명 추출
├── get_main_characters(entities)   # 주요 인물
└── get_main_locations(entities)    # 주요 장소
```

### Cell 11: 개체명 추출 실행
**기능**: 첫 챕터에서 개체명 추출  
**예상 시간**: 5-10초 (SpaCy 처리)  
**출력 예시**:
```
✓ Entity extraction completed

Main Characters:
  - Mr. Bennet: 8 mentions
  - Mrs. Bennet: 12 mentions
  - Mr. Bingley: 5 mentions

Main Locations:
  - Netherfield Park: 3 mentions
  - Hertfordshire: 2 mentions

Temporal Information:
  - this morning: 1 mentions
```

**처리 과정**:
1. SpaCy NER 모델 적용
2. PERSON, GPE, LOC, DATE, TIME 추출
3. 빈도수 계산 및 정렬

### Cell 12: ScriptFormatter 클래스
**기능**: 스크립트 형식 변환  
**예상 시간**: 즉시  
**출력 예시**:
```
✓ Script Formatter initialized
```

**클래스 메서드**:
```python
ScriptFormatter
├── extract_dialogues(text)           # 대화문 추출
├── extract_narrative(text)           # 서술 추출
└── create_scene_structure(...)       # 장면 구조화
```

### Cell 13: 장면 구조 생성
**기능**: 챕터를 장면 구조로 변환  
**예상 시간**: 5-10초  
**출력 예시**:
```
✓ Scene structure created

Scene Information:
  - Main Characters: Mr. Bennet, Mrs. Bennet, Mr. Bingley
  - Locations: Netherfield Park, Hertfordshire
  - Total Sentences: 120
  - Total Dialogues: 45

Sample Dialogues:
  1. "My dear Mr. Bennet"
  2. "have you heard that Netherfield Park is let at last?"
  3. "But it is"

Sample Narrative:
  1. It is a truth universally acknowledged, that a single man...
  2. However little known the feelings or views of such a man...
```

### Cell 14: BookToScriptPipeline 클래스
**기능**: 전체 파이프라인 통합  
**예상 시간**: 즉시  
**출력 예시**:
```
✓ Pipeline initialized
```

**파이프라인 흐름**:
```
download_book → 
clean_text → 
split_chapters → 
extract_entities → 
create_scenes → 
save_json
```

### Cell 15: 파이프라인 실행
**기능**: 샘플 도서 전체 처리  
**예상 시간**: 30-60초  
**출력 예시**:
```
Processing book 1342...
  ✓ Downloaded (743383 chars)
  ✓ Cleaned (720973 chars)
  ✓ Split into 61 chapters
  ✓ Processed 5 chapters
  ✓ Saved to ./processed_data/book_1342.json

=== Processing Summary ===

Book ID: 1342
  Total Length: 720,973 characters
  Total Chapters: 61
  Processed Chapters: 5
```

**생성 파일**:
- `./processed_data/book_1342.json`

### Cell 16: EvaluationMetrics 클래스
**기능**: BLEU 점수 계산  
**예상 시간**: 즉시  
**출력 예시**:
```
✓ Evaluation Metrics initialized

BLEU Score Examples:
  BLEU-1: 0.8889
  BLEU-2: 0.8000
  BLEU-3: 0.7143
  BLEU-4: 0.6202
```

### Cell 17: 진행 상황 저장
**기능**: 처리 결과를 JSON으로 저장  
**예상 시간**: 즉시  
**출력 예시**:
```
✓ Progress summary saved to 'progress_summary.json'

Current Status:
  Phase: Data Preprocessing
  Deadline: 2025-10-27
  Completed: 6 tasks
  Remaining: 4 tasks
```

**생성 파일**:
- `progress_summary.json`

---

## 4. 실행 결과 확인

### 4.1 생성된 파일 확인

```bash
# 처리된 데이터 확인
ls -lh ./processed_data/
# 출력: book_1342.json (약 50-100KB)

# JSON 내용 미리보기
python -c "import json; data = json.load(open('./processed_data/book_1342.json')); print(json.dumps(data, indent=2)[:500])"
```

### 4.2 통계 확인

```python
import json

# 처리 결과 로드
with open('./processed_data/book_1342.json', 'r') as f:
    result = json.load(f)

# 통계 출력
print(f"Book ID: {result['book_id']}")
print(f"Total Chapters: {result['total_chapters']}")
print(f"Processed Chapters: {len(result['processed_chapters'])}")
print(f"Total Length: {result['total_length']:,} characters")

# 첫 챕터 정보
first_chapter = result['processed_chapters'][0]
print(f"\nFirst Chapter: {first_chapter['chapter_title']}")
print(f"Characters: {len(first_chapter['entities']['PERSON'])}")
print(f"Locations: {len(first_chapter['entities']['GPE']) + len(first_chapter['entities']['LOC'])}")
print(f"Dialogues: {first_chapter['scene_data']['total_dialogues']}")
```

### 4.3 데이터 품질 확인

```python
# 챕터 길이 분포
lengths = [len(ch['original_text']) for ch in result['processed_chapters']]
print(f"Average chapter length: {sum(lengths)/len(lengths):.0f} chars")
print(f"Min: {min(lengths)}, Max: {max(lengths)}")

# 개체명 수
total_persons = sum(len(ch['entities']['PERSON']) for ch in result['processed_chapters'])
print(f"Total unique characters: {total_persons}")
```

---

## 5. 문제 해결

### 5.1 일반적인 오류

#### 오류 1: ModuleNotFoundError
```
ModuleNotFoundError: No module named 'spacy'
```

**해결**:
```bash
pip install spacy
python -m spacy download en_core_web_sm
```

#### 오류 2: 다운로드 실패
```
Failed to download book 1342: Status 503
```

**해결**:
```python
# 다른 도서 ID 시도
book_id = 84  # The Adventures of Tom Sawyer
# 또는 재시도
import time
time.sleep(5)  # 5초 대기 후 재시도
```

#### 오류 3: 메모리 부족
```
MemoryError: Unable to allocate array
```

**해결**:
```python
# SpaCy max_length 제한
extractor.nlp.max_length = 500000  # 50만 자로 제한

# 배치 크기 줄이기
pipeline.process_multiple_books(book_ids[:5])  # 한 번에 5권만
```

#### 오류 4: 챕터 분할 실패
```
✓ Found 1 chapters (Full Text)
```

**해결**:
```python
# 디버깅 셀 실행하여 패턴 확인
# 텍스트 샘플 확인
print(cleaned_text[:2000])

# 수동 패턴 확인
import re
matches = re.findall(r'\n\s*(CHAPTER|Chapter)\s+([IVXLCDM]+|\d+)', cleaned_text)
print(f"Matches: {len(matches)}")
```

### 5.2 성능 최적화

#### 느린 실행 속도
```python
# 병렬 처리
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(pipeline.process_book, book_ids))
```

#### GPU 활용 (선택)
```python
import torch

# CUDA 사용 가능 확인
if torch.cuda.is_available():
    device = torch.device("cuda")
    print(f"Using GPU: {torch.cuda.get_device_name(0)}")
else:
    device = torch.device("cpu")
    print("Using CPU")
```

### 5.3 데이터 검증

```python
def validate_processed_data(result):
    """처리된 데이터 검증"""
    checks = {
        'has_chapters': result['total_chapters'] > 1,
        'has_processed': len(result['processed_chapters']) > 0,
        'has_entities': any(ch['entities']['PERSON'] for ch in result['processed_chapters']),
        'has_dialogues': any(ch['scene_data']['total_dialogues'] > 0 for ch in result['processed_chapters'])
    }
    
    print("Validation Results:")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
    
    return all(checks.values())

# 사용
is_valid = validate_processed_data(result)
print(f"\nOverall: {'✅ PASSED' if is_valid else '❌ FAILED'}")
```

---

## 6. 다음 단계

### 6.1 더 많은 도서 처리

```python
# 인기 도서 50권 처리
collector = GutenbergCollector()
book_ids = collector.get_popular_books(limit=50)

pipeline = BookToScriptPipeline()
results = pipeline.process_multiple_books(book_ids, output_dir='./processed_data')

print(f"Successfully processed {len(results)} books")
```

### 6.2 학습 데이터셋 생성

```python
from sklearn.model_selection import train_test_split
import json

# 모든 챕터 수집
all_chapters = []
for result in results:
    for chapter in result['processed_chapters']:
        all_chapters.append({
            'input': chapter['original_text'],
            'output': chapter['scene_data'],
            'metadata': {
                'book_id': result['book_id'],
                'chapter': chapter['chapter_number']
            }
        })

# 분할
train, temp = train_test_split(all_chapters, test_size=0.2, random_state=42)
val, test = train_test_split(temp, test_size=0.5, random_state=42)

# 저장
with open('train_data.json', 'w') as f:
    json.dump(train, f, ensure_ascii=False, indent=2)
with open('val_data.json', 'w') as f:
    json.dump(val, f, ensure_ascii=False, indent=2)
with open('test_data.json', 'w') as f:
    json.dump(test, f, ensure_ascii=False, indent=2)

print(f"Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")
```

### 6.3 진행 상황 추적

```bash
# 진행 상황 확인
python track_progress.py --scan
python track_progress.py --check

# 일일 보고서 생성
python track_progress.py --report
```

---

## 요약

### ✅ 실행 체크리스트

- [ ] 환경 설정 완료 (라이브러리 설치)
- [ ] SpaCy 모델 다운로드
- [ ] NLTK 데이터 다운로드
- [ ] 노트북 전체 실행 성공
- [ ] 샘플 도서 처리 확인
- [ ] JSON 파일 생성 확인
- [ ] 데이터 품질 검증

### 📊 예상 결과

- **처리 시간**: 샘플 1권당 30-60초
- **출력 파일**: JSON 형식 (50-100KB per book)
- **챕터 수**: 도서마다 다름 (평균 20-100개)
- **정확도**: 95%+ 챕터 분할 성공률

### 🎯 성공 기준

✅ 챕터 > 1개  
✅ 첫 챕터 제목 ≠ "Full Text"  
✅ 개체명 추출 성공  
✅ 대화문 추출 성공  
✅ JSON 파일 생성 완료

---

**문서 버전**: 1.0  
**작성일**: 2025-10-12  
**다음 업데이트**: 피드백 반영 후

**문의사항**: GitHub Issues 또는 팀 채팅방
