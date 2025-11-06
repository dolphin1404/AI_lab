# 데이터 수집 및 전처리 파이프라인 상세 문서

> **작성일**: 2025년 10월 14일  
> **프로젝트**: 도서-스크립트 변환 LLM 모델 개발  
> **목적**: GitHub 이슈 및 기술 문서용

---

## 📋 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [데이터 수집 방법](#2-데이터-수집-방법)
3. [전처리 파이프라인](#3-전처리-파이프라인)
4. [구현 세부사항](#4-구현-세부사항)
5. [학습 데이터셋 생성](#5-학습-데이터셋-생성)
6. [품질 검증](#6-품질-검증)
7. [실행 방법](#7-실행-방법)
8. [문제 해결](#8-문제-해결)

---

## 1. 프로젝트 개요

### 1.1 목표
도서 텍스트를 비디오 스크립트 형식으로 변환하는 LLM 모델을 위한 데이터셋 구축

### 1.2 데이터 소스
- **출처**: Project Gutenberg (https://www.gutenberg.org/)
- **라이선스**: 퍼블릭 도메인
- **도서 수**: 10권 (확장 가능)
- **장르**: 고전 영문 소설

### 1.3 선정 도서 목록

| Book ID | 제목 | 저자 | 예상 챕터 수 |
|---------|------|------|--------------|
| 1342 | Pride and Prejudice | Jane Austen | 61 |
| 2701 | Moby Dick | Herman Melville | 135 |
| 84 | Frankenstein | Mary Shelley | 24 |
| 1661 | The Adventures of Sherlock Holmes | Arthur Conan Doyle | 12 |
| 11 | Alice's Adventures in Wonderland | Lewis Carroll | 12 |
| 98 | A Tale of Two Cities | Charles Dickens | 45 |
| 74 | The Adventures of Tom Sawyer | Mark Twain | 35 |
| 345 | Dracula | Bram Stoker | 27 |
| 46 | A Christmas Carol | Charles Dickens | 5 |
| 1952 | The Yellow Wallpaper | Charlotte Perkins Gilman | 1 |

**총 예상 샘플 수**: 약 357개 챕터 (실제 처리 결과에 따라 변동)

---

## 2. 데이터 수집 방법

### 2.1 GutenbergCollector 클래스

#### 주요 기능
```python
class GutenbergCollector:
    def __init__(self):
        self.base_url = "https://www.gutenberg.org/files/"
        self.cache_dir = "./gutenberg_cache"
    
    def download_book(self, book_id):
        # 캐시 확인 → 다운로드 → 저장
        pass
```

#### 다운로드 로직

1. **캐시 확인**
   - 먼저 `./gutenberg_cache/book_{id}.txt` 파일 존재 확인
   - 캐시가 있으면 파일에서 읽기 (네트워크 요청 절약)

2. **네트워크 다운로드**
   - URL 패턴 1: `https://www.gutenberg.org/files/{id}/{id}-0.txt`
   - URL 패턴 2 (실패 시): `https://www.gutenberg.org/files/{id}/{id}.txt`
   - `requests.get()` with 30초 타임아웃

3. **저장**
   - UTF-8 인코딩으로 캐시 디렉토리에 저장
   - 다음 실행 시 재사용

#### 에러 처리
```python
try:
    # 메인 URL 시도
    response = requests.get(url, timeout=30)
    response.raise_for_status()
except Exception as e:
    # 대체 URL 시도
    alt_response = requests.get(alt_url, timeout=30)
```

### 2.2 데이터 수집 결과

**예상 결과물**:
```
gutenberg_cache/
├── book_1342.txt  (717 KB)
├── book_2701.txt  (1.2 MB)
├── book_84.txt    (448 KB)
├── book_1661.txt  (594 KB)
├── book_11.txt    (170 KB)
├── book_98.txt    (788 KB)
├── book_74.txt    (408 KB)
├── book_345.txt   (881 KB)
├── book_46.txt    (176 KB)
└── book_1952.txt  (63 KB)

Total: ~5.4 MB
```

---

## 3. 전처리 파이프라인

### 3.1 파이프라인 아키텍처

```
원본 텍스트 (Raw Text)
    ↓
┌─────────────────────────────────────┐
│  1. Gutenberg 헤더/푸터 제거         │
│     - START/END 마커 감지            │
│     - 저작권 정보 제거               │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  2. 기본 텍스트 정제                 │
│     - 과도한 공백 제거               │
│     - 줄바꿈 정규화                  │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  3. 목차(TOC) 제거                   │
│     - "CONTENTS" 섹션 감지           │
│     - 실제 챕터와 구분               │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  4. 챕터 분할                        │
│     - 정규표현식 패턴 매칭           │
│     - 여러 패턴 시도 및 검증         │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  5. 개체명 추출 (NER)                │
│     - SpaCy en_core_web_sm           │
│     - PERSON, GPE, LOC, DATE 등      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  6. 스크립트 구조화                  │
│     - 대화문 추출                    │
│     - 서술 문장 분리                 │
│     - 씬 정보 구성                   │
└─────────────────────────────────────┘
    ↓
학습 데이터셋 (Training Dataset)
```

### 3.2 TextPreprocessor 클래스

#### 3.2.1 헤더/푸터 제거

**목적**: Project Gutenberg의 메타데이터 제거

**구현**:
```python
def remove_gutenberg_header_footer(self, text):
    start_markers = [
        "*** START OF THIS PROJECT GUTENBERG",
        "*** START OF THE PROJECT GUTENBERG",
        "***START OF THE PROJECT GUTENBERG"
    ]
    end_markers = [
        "*** END OF THIS PROJECT GUTENBERG",
        "*** END OF THE PROJECT GUTENBERG",
        "***END OF THE PROJECT GUTENBERG"
    ]
    # 마커 사이의 텍스트만 추출
```

**효과**:
- 평균 ~5-10% 텍스트 제거
- 라이선스 정보, 기부 안내 등 제거

#### 3.2.2 목차 제거 (개선 버전 v4)

**목적**: 실제 챕터 내용만 보존, 목차 항목 제거

**알고리즘**:
```python
def remove_table_of_contents(self, text):
    # 1. 목차 시작 감지
    #    - "CONTENTS", "TABLE OF CONTENTS" 단독 라인
    #    - "Heading to Chapter" 패턴 연속 2줄 이상
    
    # 2. 실제 챕터 확인
    #    - "CHAPTER X" 패턴 매칭
    #    - 다음 10줄 내 40자 이상 문장 확인
    #    - 목차 키워드 없음 확인
    
    # 3. 목차 종료
    #    - 첫 실제 챕터 발견 시
    #    - 또는 150줄 초과 시
```

**개선 사항**:
- ✅ Pride and Prejudice의 "Heading to Chapter" 패턴 처리
- ✅ 실제 챕터와 목차 항목 구분 강화
- ✅ False positive 감소 (목차가 아닌데 제거되는 경우)

#### 3.2.3 챕터 분할 (개선 버전 v2)

**지원 패턴**:
1. `CHAPTER I`, `Chapter 1`, `CHAPTER ONE`
2. `BOOK I`, `PART I`
3. 챕터 제목 포함: `CHAPTER I. The Beginning`

**알고리즘**:
```python
def split_into_chapters(self, text):
    # 1단계: 목차 제거
    text_without_toc = self.remove_table_of_contents(text)
    
    # 2단계: 여러 패턴 시도
    patterns = [
        r'\n\s*(CHAPTER|Chapter)\s+([IVXLCDM]+|\d+|One|Two|...)',
        r'\n\s*(BOOK|Book|PART|Part)\s+([IVXLCDM]+|\d+)',
    ]
    
    # 3단계: 최적 패턴 선택
    #   - 2-150개 챕터
    #   - 평균 길이 300자 이상
    #   - 최대 챕터 수 우선
    
    # 4단계: 챕터 추출 및 검증
    #   - 내용 길이 200자 이상
    #   - 제목 추출 (첫 줄 60자 이하)
```

**타임아웃 처리**:
- 각 패턴당 3초 제한
- Catastrophic backtracking 방지

**Fallback 메커니즘**:
- 정규식 실패 시 줄 단위 분석
- 수동 챕터 마커 탐지

**검증 기준**:
- ✅ 최소 2개 이상의 챕터
- ✅ 평균 챕터 길이 300자 이상
- ✅ 실제 내용 포함 확인

### 3.3 EntityExtractor 클래스

#### 3.3.1 SpaCy NER 파이프라인

**모델**: `en_core_web_sm`
- 크기: 13 MB
- 정확도: ~85% (일반 텍스트)
- 처리 속도: ~1,000 단어/초

**추출 개체 유형**:
```python
entities = {
    'PERSON': [],   # 인물 (Elizabeth, Darcy)
    'GPE': [],      # 지정학적 개체 (London, England)
    'LOC': [],      # 위치 (Netherfield Park)
    'DATE': [],     # 날짜 (November, 1813)
    'TIME': [],     # 시간 (morning, evening)
    'ORG': [],      # 조직 (None in novels)
    'EVENT': []     # 이벤트 (Ball, Wedding)
}
```

#### 3.3.2 빈도수 계산

**방법**:
```python
# 중복 제거 및 빈도수 집계
entity_counts = defaultdict(int)
for entity in entities[category]:
    entity_counts[entity] += 1

# 빈도순 정렬
sorted_entities = sorted(
    entity_counts.items(), 
    key=lambda x: x[1], 
    reverse=True
)
```

**예시 출력** (Pride and Prejudice, Chapter 1):
```
PERSON: [('Elizabeth', 15), ('Darcy', 12), ('Mr. Bennet', 8), ...]
GPE: [('Netherfield', 5), ('Meryton', 3), ('London', 2)]
LOC: [('Longbourn', 4), ('Park', 2)]
```

### 3.4 ScriptFormatter 클래스

#### 3.4.1 대화문 추출

**패턴**:
```python
dialogue_pattern = r'["\']([^"\']+)["\']'
dialogues = re.findall(dialogue_pattern, text)
```

**필터링**:
- 최소 3단어 이상
- 특수문자만 있는 경우 제외

**예시**:
```python
# 입력
"How do you do?" said Mr. Darcy.
"I am well, thank you," replied Elizabeth.

# 출력
['How do you do?', 'I am well, thank you']
```

#### 3.4.2 서술 추출

**방법**:
```python
# 대화문 제거
narrative = re.sub(r'["\'][^"\']+["\']', '', text)
# 정제
narrative = re.sub(r' +', ' ', narrative)
```

**예시**:
```python
# 입력
She walked into the room. "Hello," she said.

# 출력 (서술만)
She walked into the room.  she said.
```

#### 3.4.3 씬 구조 생성

**구성 요소**:
```python
scene_data = {
    'characters': top_5_characters,
    'locations': top_3_locations,
    'dialogues': first_10_dialogues,
    'narrative_sentences': first_20_sentences,
    'total_sentences': count,
    'total_dialogues': count
}
```

---

## 4. 구현 세부사항

### 4.1 BookToScriptPipeline 클래스

**전체 워크플로우**:

```python
class BookToScriptPipeline:
    def process_book(self, book_id):
        # 1. 다운로드
        book_text = self.collector.download_book(book_id)
        
        # 2. 전처리
        cleaned_text = self.preprocessor.remove_gutenberg_header_footer(book_text)
        cleaned_text = self.preprocessor.clean_text(cleaned_text)
        
        # 3. 챕터 분할
        chapters = self.preprocessor.split_into_chapters(cleaned_text)
        
        # 4. 각 챕터 처리 (처음 5개만)
        for chapter in chapters[:5]:
            # 개체명 추출
            entities = self.extractor.extract_entities(chapter['content'])
            
            # 씬 구조 생성
            scene_data = self.formatter.create_scene_structure(
                chapter['content'], 
                entities
            )
        
        return processed_data
```

**처리 제한**:
- 챕터당 처음 5개만 처리 (메모리 및 시간 절약)
- 전체 처리는 `process_multiple_books()` 사용

### 4.2 메모리 최적화

**SpaCy max_length 설정**:
```python
self.nlp.max_length = 1000000  # 1MB
text_to_process = text[:1000000]  # 초과 시 잘라내기
```

**이유**:
- SpaCy 기본 제한: 1,000,000 문자
- Moby Dick 같은 긴 책 처리 가능

---

## 5. 학습 데이터셋 생성

### 5.1 DatasetBuilder 클래스

#### 5.1.1 학습 샘플 생성

**입력 포맷**:
```python
input_text = f"""Convert the following book chapter into a video script format. 
Extract key elements including characters, locations, dialogues, and narrative descriptions.

Chapter: {chapter_title}

Text:
{chapter_text[:2000]}"""  # 처음 2000자
```

**출력 포맷** (JSON):
```json
{
  "scene_title": "CHAPTER I",
  "characters": ["Elizabeth", "Darcy", "Mr. Bennet"],
  "locations": ["Longbourn", "Netherfield"],
  "dialogues": [
    "How do you do?",
    "I am well, thank you"
  ],
  "narrative": "She walked into the room. He stood by the window.",
  "total_sentences": 45,
  "total_dialogues": 12
}
```

**토큰 제한 고려**:
- 입력: 처음 2000자 (약 400 토큰)
- LLM 토큰 제한 대응 (GPT-2: 1024, T5: 512)

#### 5.1.2 데이터셋 분할

**비율**:
- Train: 80%
- Validation: 10%
- Test: 10%

**코드**:
```python
from sklearn.model_selection import train_test_split

# 첫 번째 분할
train_data, temp_data = train_test_split(
    samples, test_size=0.2, random_state=42
)

# 두 번째 분할
val_data, test_data = train_test_split(
    temp_data, test_size=0.5, random_state=42
)
```

**랜덤 시드**: 42 (재현성)

#### 5.1.3 저장

**파일 형식**: JSON
**인코딩**: UTF-8
**들여쓰기**: 2칸 (가독성)

**파일 구조**:
```json
[
  {
    "input": "Convert the following book chapter...",
    "output": "{\"scene_title\": \"CHAPTER I\", ...}",
    "metadata": {
      "book_id": 1342,
      "chapter_number": 1,
      "chapter_title": "CHAPTER I",
      "input_length": 1850,
      "output_length": 423
    }
  },
  ...
]
```

### 5.2 예상 데이터셋 크기

**계산**:
- 도서 수: 10권
- 평균 챕터: 35개/권
- 총 챕터: 350개

**실제 (처음 5챕터만)**:
- 처리 챕터: 50개 (10권 × 5챕터)
- Train: 40 샘플
- Val: 5 샘플
- Test: 5 샘플

**파일 크기** (예상):
- train_data.json: ~2.5 MB
- val_data.json: ~300 KB
- test_data.json: ~300 KB

---

## 6. 품질 검증

### 6.1 자동 검증

**체크 항목**:
1. ✅ 모든 샘플에 입력/출력 존재
2. ✅ 입력 길이 > 100자
3. ✅ 출력이 유효한 JSON
4. ✅ 필수 필드 존재 (characters, locations, dialogues)
5. ✅ 메타데이터 완전성

**코드**:
```python
def validate_sample(sample):
    assert 'input' in sample
    assert 'output' in sample
    assert len(sample['input']) > 100
    
    output_data = json.loads(sample['output'])
    assert 'scene_title' in output_data
    assert 'characters' in output_data
    # ...
```

### 6.2 수동 검증

**샘플 리뷰**:
- 랜덤 10개 샘플 추출
- 입력-출력 정합성 확인
- 개체명 정확도 확인

**품질 기준**:
- 인물 추출 정확도: >85%
- 장소 추출 정확도: >75%
- 대화문 추출 정확도: >90%

### 6.3 통계 분석

**계산 지표**:
```python
statistics = {
    'total_samples': len(training_samples),
    'avg_input_length': mean(input_lengths),
    'avg_output_length': mean(output_lengths),
    'books_processed': len(unique_book_ids),
    'chapters_processed': total_chapters,
    'avg_chapters_per_book': chapters / books
}
```

---

## 7. 실행 방법

### 7.1 환경 설정

```bash
# 1. 필수 라이브러리 설치
pip install requests beautifulsoup4 nltk spacy scikit-learn

# 2. SpaCy 모델 다운로드
python -m spacy download en_core_web_sm

# 3. NLTK 데이터
python -c "import nltk; nltk.download('punkt')"
```

### 7.2 노트북 실행

```bash
# Jupyter Notebook 실행
jupyter notebook data_preprocessing.ipynb
```

**실행 순서**:
1. 셀 1-5: 환경 설정 및 라이브러리 임포트
2. 셀 6-9: 데이터 수집 (GutenbergCollector)
3. 셀 10-12: 전처리 (TextPreprocessor)
4. 셀 13-15: 개체명 추출 (EntityExtractor)
5. 셀 16-18: 스크립트 변환 (ScriptFormatter)
6. 셀 19-21: 파이프라인 실행
7. 셀 22-24: 데이터셋 생성 (DatasetBuilder)
8. 셀 25: 통계 및 검증

### 7.3 배치 처리

```python
# 전체 도서 처리
results = pipeline.process_multiple_books(
    book_ids_to_process,
    output_dir='./processed_data'
)

# 학습 데이터 생성
training_samples = dataset_builder.create_training_samples(results)
train, val, test = dataset_builder.split_dataset(training_samples)
dataset_builder.save_datasets(train, val, test)
```

**예상 실행 시간**:
- 다운로드: ~2-5분 (캐시 없을 때)
- 전처리: ~10-15분 (10권)
- 학습 데이터 생성: ~1-2분

**총 소요 시간**: 약 15-20분

---

## 8. 문제 해결

### 8.1 자주 발생하는 오류

#### 오류 1: `NameError: name 'collector' is not defined`

**원인**: 셀 실행 순서 문제

**해결**:
```python
# GutenbergCollector 초기화 셀을 먼저 실행
collector = GutenbergCollector()
```

#### 오류 2: 다운로드 실패

**원인**: 
- 네트워크 연결 문제
- Gutenberg 서버 접속 불가
- 잘못된 Book ID

**해결**:
```python
# 다운로드 재시도
book_text = collector.download_book(book_id)

# 또는 다른 Book ID 시도
alternative_id = 1342  # Pride and Prejudice (안정적)
```

#### 오류 3: `OSError: [E050] Can't find model 'en_core_web_sm'`

**원인**: SpaCy 모델 미설치

**해결**:
```bash
python -m spacy download en_core_web_sm
```

#### 오류 4: 메모리 부족

**원인**: 큰 책 처리 시 메모리 초과

**해결**:
```python
# max_length 제한
self.nlp.max_length = 500000  # 500KB로 감소

# 또는 챕터 수 제한
chapters = chapters[:3]  # 처음 3개만
```

### 8.2 성능 최적화

#### 캐시 활용

```python
# 캐시 디렉토리 확인
if os.path.exists('gutenberg_cache'):
    print("캐시 사용 가능")
```

#### 병렬 처리 (선택)

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(
        pipeline.process_book, 
        book_ids_to_process
    ))
```

### 8.3 데이터 품질 이슈

#### 챕터 감지 실패

**증상**: 챕터가 1개로 인식됨

**해결**:
1. 텍스트 샘플 확인
2. 챕터 패턴 확인
3. Fallback 메커니즘 사용
4. 수동 분할 고려

#### 개체명 추출 부정확

**증상**: 인물/장소가 잘못 인식됨

**원인**: 
- SpaCy 모델 한계 (문학 텍스트)
- 고유명사 불명확

**개선**:
- 더 큰 모델 사용 (`en_core_web_md`, `en_core_web_lg`)
- 후처리 필터링
- 빈도수 기반 필터링

---

## 9. 다음 단계

### 9.1 모델 선택

**추천 모델**:
1. **T5-base** (주력)
   - Text-to-Text 변환에 최적
   - 220M 파라미터
   - Seq2Seq 아키텍처

2. **BART-base** (대안)
   - 텍스트 생성 강점
   - 140M 파라미터

3. **GPT-2** (베이스라인)
   - 빠른 학습
   - 117M 파라미터

### 9.2 Fine-tuning 준비

```python
from transformers import T5ForConditionalGeneration, T5Tokenizer

# 모델 로드
model = T5ForConditionalGeneration.from_pretrained('t5-base')
tokenizer = T5Tokenizer.from_pretrained('t5-base')

# 데이터 로드
import json
with open('train_data.json', 'r') as f:
    train_data = json.load(f)

# 토큰화
train_encodings = tokenizer(
    [s['input'] for s in train_data],
    truncation=True,
    padding=True,
    max_length=512
)
```

### 9.3 학습 계획

**하이퍼파라미터**:
- Learning rate: 5e-5
- Batch size: 4 (GPU 메모리에 따라)
- Epochs: 3-5
- Warmup steps: 500

**예상 학습 시간**:
- Tesla T4 GPU: ~2-3시간
- CPU: ~10-15시간

---

## 10. 참고 자료

### 10.1 라이브러리 문서

- SpaCy: https://spacy.io/
- NLTK: https://www.nltk.org/
- Transformers: https://huggingface.co/docs/transformers/

### 10.2 학술 자료

- BLEU Score: Papineni et al. (2002)
- NER: Sang & De Meulder (2003)
- T5: Raffel et al. (2020)

### 10.3 관련 프로젝트

- Gutenberg API: https://github.com/c-w/gutenberg
- Book-to-Script: [이 프로젝트]

---

## 부록 A: 전체 클래스 다이어그램

```
GutenbergCollector
├── download_book()
└── cache_dir

TextPreprocessor
├── remove_gutenberg_header_footer()
├── remove_table_of_contents()
├── clean_text()
├── split_into_chapters()
└── _fallback_chapter_split()

EntityExtractor
├── extract_entities()
├── get_main_characters()
└── get_main_locations()

ScriptFormatter
├── extract_dialogues()
├── extract_narrative()
└── create_scene_structure()

BookToScriptPipeline
├── collector: GutenbergCollector
├── preprocessor: TextPreprocessor
├── extractor: EntityExtractor
├── formatter: ScriptFormatter
├── process_book()
└── process_multiple_books()

DatasetBuilder
├── create_training_samples()
├── split_dataset()
└── save_datasets()

EvaluationMetrics
├── calculate_bleu()
└── calculate_bleu_variants()
```

---

## 부록 B: 데이터 예시

### 입력 예시 (Pride and Prejudice, Chapter 1)

```
Convert the following book chapter into a video script format. 
Extract key elements including characters, locations, dialogues, and narrative descriptions.

Chapter: CHAPTER I

Text:
It is a truth universally acknowledged, that a single man in possession
of a good fortune, must be in want of a wife.

However little known the feelings or views of such a man may be on his
first entering a neighbourhood, this truth is so well fixed in the minds
of the surrounding families, that he is considered the rightful property
of some one or other of their daughters.

"My dear Mr. Bennet," said his lady to him one day, "have you heard that
Netherfield Park is let at last?"

Mr. Bennet replied that he had not.

"But it is," returned she; "for Mrs. Long has just been here, and she
told me all about it."
...
```

### 출력 예시

```json
{
  "scene_title": "CHAPTER I",
  "characters": [
    "Mr. Bennet",
    "Mrs. Bennet",
    "Mrs. Long"
  ],
  "locations": [
    "Netherfield Park"
  ],
  "dialogues": [
    "My dear Mr. Bennet, have you heard that Netherfield Park is let at last?",
    "But it is, for Mrs. Long has just been here, and she told me all about it."
  ],
  "narrative": "It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife. However little known the feelings or views of such a man may be on his first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families, that he is considered the rightful property of some one or other of their daughters. Mr. Bennet replied that he had not.",
  "total_sentences": 45,
  "total_dialogues": 12
}
```

---

**문서 버전**: 1.0  
**최종 업데이트**: 2025년 10월 14일
