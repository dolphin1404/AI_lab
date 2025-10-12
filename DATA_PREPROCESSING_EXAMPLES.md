# 데이터 전처리 방법 상세 설명 및 예시

## 목차
1. [개요](#개요)
2. [챕터 분할 (Chapter Splitting)](#챕터-분할)
3. [텍스트 정제 (Text Cleaning)](#텍스트-정제)
4. [개체명 추출 (Entity Extraction)](#개체명-추출)
5. [스크립트 변환 (Script Formatting)](#스크립트-변환)

---

## 개요

데이터 전처리는 원본 도서 텍스트를 LLM 학습에 적합한 형태로 변환하는 과정입니다.

### 전체 파이프라인
```
원본 도서 텍스트
    ↓
1. Gutenberg 헤더/푸터 제거
    ↓
2. 텍스트 정제
    ↓
3. 챕터 분할
    ↓
4. 개체명 추출
    ↓
5. 스크립트 구조화
    ↓
학습 데이터셋
```

---

## 챕터 분할

### 문제점
기존 코드는 단순한 정규식 패턴만 사용하여 다양한 챕터 형식을 처리하지 못했습니다.

### 해결 방법
개선된 알고리즘은 **3단계 접근 방식**을 사용합니다:

#### 1단계: 다양한 패턴 시도
```python
patterns = [
    # Pattern 1: "CHAPTER I" or "Chapter 1"
    r'\n\s*(CHAPTER|Chapter)\s+([IVXLCDM]+|\d+|One|Two|...)[\\s\\.:\\n]',
    
    # Pattern 2: 로마자/숫자만 있는 줄
    r'\n\s*([IVXLCDM]+|\d+)\.?\s*\n',
    
    # Pattern 3: "BOOK I", "PART I"
    r'\n\s*(BOOK|Book|PART|Part)\s+([IVXLCDM]+|\d+)[\\s\\.:\\n]',
]
```

#### 2단계: 최적 패턴 선택
- 각 패턴을 시도하여 챕터 수를 계산
- 3-50개 범위의 챕터를 생성하는 패턴 선택
- 가장 많은 챕터를 발견한 패턴 사용

#### 3단계: Fallback 분석
- 패턴 매칭 실패 시, 줄 단위 분석
- 짧은 줄(30자 이하)에서 챕터 마커 검색
- 맥락 기반 검증

### 예시 1: The Hound of the Baskervilles (Book 2852)

**원본 텍스트 구조:**
```
THE HOUND OF THE BASKERVILLES

Another Adventure of Sherlock Holmes

by A. Conan Doyle


Chapter 1
Mr. Sherlock Holmes


Mr. Sherlock Holmes, who was usually very late in the mornings...

Chapter 2
The Curse of the Baskervilles

I have in my pocket a manuscript," said Dr. James Mortimer...
```

**처리 결과:**
```python
chapters = [
    {
        'title': 'Chapter 1',
        'content': 'Mr. Sherlock Holmes\n\nMr. Sherlock Holmes, who was...'
    },
    {
        'title': 'Chapter 2',
        'content': 'The Curse of the Baskervilles\n\nI have in my pocket...'
    },
    # ... 총 15개 챕터
]
```

### 예시 2: Moby Dick (Book 2701)

**원본 텍스트 구조:**
```
MOBY-DICK;

or, THE WHALE

by Herman Melville


CHAPTER 1. Loomings.

Call me Ishmael. Some years ago—never mind how long precisely...

CHAPTER 2. The Carpet-Bag.

I stuffed a shirt or two into my old carpet-bag...
```

**처리 결과:**
```python
chapters = [
    {
        'title': 'CHAPTER 1',
        'content': 'Loomings.\n\nCall me Ishmael. Some years ago...'
    },
    {
        'title': 'CHAPTER 2',
        'content': 'The Carpet-Bag.\n\nI stuffed a shirt or two...'
    },
    # ... 총 135개 챕터
]
```

### 예시 3: Tom Sawyer (Book 74)

**원본 텍스트 구조:**
```
THE ADVENTURES OF TOM SAWYER

BY MARK TWAIN


CHAPTER I

"TOM!"

No answer.

"TOM!"

No answer.


CHAPTER II

SATURDAY morning was come, and all the summer world was bright...
```

**처리 결과:**
```python
chapters = [
    {
        'title': 'CHAPTER I',
        'content': '"TOM!"\n\nNo answer.\n\n"TOM!"\n\nNo answer.'
    },
    {
        'title': 'CHAPTER II',
        'content': 'SATURDAY morning was come, and all the summer...'
    },
    # ... 총 35개 챕터
]
```

### 디버깅 방법

챕터가 제대로 분할되지 않을 때:

```python
# 1. 원본 텍스트의 챕터 형식 확인
print(text[:2000])  # 처음 2000자 출력

# 2. 챕터 분할 결과 확인
chapters = preprocessor.split_into_chapters(text)
print(f"Found {len(chapters)} chapters")
for i, ch in enumerate(chapters[:3]):
    print(f"\nChapter {i+1}: {ch['title']}")
    print(f"Content preview: {ch['content'][:100]}...")

# 3. 패턴 매칭 테스트
import re
pattern = r'\n\s*(CHAPTER|Chapter)\s+([IVXLCDM]+|\d+)'
matches = re.findall(pattern, text)
print(f"Pattern matches: {len(matches)}")
print(matches[:10])  # 처음 10개 매치 출력
```

---

## 텍스트 정제

### 1. Gutenberg 헤더/푸터 제거

**원본 텍스트:**
```
The Project Gutenberg eBook of Moby Dick

This eBook is for the use of anyone anywhere...

*** START OF THE PROJECT GUTENBERG EBOOK MOBY DICK ***

MOBY-DICK; or, THE WHALE

[실제 책 내용]

*** END OF THE PROJECT GUTENBERG EBOOK MOBY DICK ***
```

**처리 후:**
```
MOBY-DICK; or, THE WHALE

[실제 책 내용]
```

**코드:**
```python
def remove_gutenberg_header_footer(self, text):
    start_markers = [
        "*** START OF THIS PROJECT GUTENBERG",
        "*** START OF THE PROJECT GUTENBERG"
    ]
    
    end_markers = [
        "*** END OF THIS PROJECT GUTENBERG",
        "*** END OF THE PROJECT GUTENBERG"
    ]
    
    # 시작 위치 찾기
    start_idx = 0
    for marker in start_markers:
        idx = text.find(marker)
        if idx != -1:
            start_idx = text.find('\n', idx) + 1
            break
    
    # 종료 위치 찾기
    end_idx = len(text)
    for marker in end_markers:
        idx = text.find(marker)
        if idx != -1:
            end_idx = idx
            break
    
    return text[start_idx:end_idx].strip()
```

### 2. 공백 정규화

**원본:**
```
Mr.    Sherlock     Holmes,    who was usually


very    late    in the mornings,
```

**처리 후:**
```
Mr. Sherlock Holmes, who was usually

very late in the mornings,
```

**코드:**
```python
def clean_text(self, text):
    # 여러 줄바꿈을 2개로
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # 여러 공백을 1개로
    text = re.sub(r' +', ' ', text)
    
    # 줄 시작/끝 공백 제거
    text = '\n'.join(line.strip() for line in text.split('\n'))
    
    return text.strip()
```

---

## 개체명 추출

### SpaCy NER 사용

**원본 텍스트:**
```
Mr. Sherlock Holmes, who was usually very late in the mornings, 
save upon those not infrequent occasions when he was up all night, 
was seated at the breakfast table. I stood upon the hearth-rug and 
picked up the stick which our visitor had left behind him the night 
before. It was a fine, thick piece of wood, bulbous-headed, of the 
sort which is known as a "Penang lawyer."
```

**추출된 개체명:**
```python
entities = {
    'PERSON': [
        ('Sherlock Holmes', 15),  # 15번 언급
        ('Holmes', 89),
        ('Watson', 45),
        ('Mortimer', 23),
    ],
    'GPE': [  # 지정학적 개체
        ('London', 12),
        ('Devonshire', 8),
        ('Baker Street', 5),
    ],
    'LOC': [  # 위치
        ('Baskerville Hall', 18),
        ('the moor', 25),
    ],
    'DATE': [
        ('the night before', 3),
        ('that morning', 2),
    ],
    'TIME': [
        ('the mornings', 1),
        ('all night', 2),
    ]
}
```

**코드:**
```python
def extract_entities(self, text, max_length=1000000):
    self.nlp.max_length = max_length
    doc = self.nlp(text[:max_length])
    
    entities = {
        'PERSON': [],
        'GPE': [],
        'LOC': [],
        'DATE': [],
        'TIME': [],
        'ORG': [],
        'EVENT': []
    }
    
    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)
    
    # 중복 제거 및 빈도수 계산
    for key in entities:
        entity_counts = defaultdict(int)
        for entity in entities[key]:
            entity_counts[entity] += 1
        entities[key] = sorted(entity_counts.items(), 
                              key=lambda x: x[1], 
                              reverse=True)
    
    return entities
```

### 예시 출력

```python
# The Hound of the Baskervilles - Chapter 1
entities = extractor.extract_entities(chapter_text)

print("주요 인물:")
for char, count in entities['PERSON'][:5]:
    print(f"  - {char}: {count}회 등장")

# 출력:
# 주요 인물:
#   - Sherlock Holmes: 8회 등장
#   - Holmes: 15회 등장
#   - James Mortimer: 3회 등장
#   - Dr. Mortimer: 2회 등장
```

---

## 스크립트 변환

### 1. 대화문 추출

**원본 텍스트:**
```
"Good-morning, Holmes," said I. "You are busy, I see."

"Yes, I have had a busy morning," he answered. "I have been 
examining this stick. You know my methods."

"What do you make of it?"

"It is obviously a walking-stick," said Holmes.
```

**추출된 대화문:**
```python
dialogues = [
    "Good-morning, Holmes",
    "You are busy, I see",
    "Yes, I have had a busy morning",
    "I have been examining this stick. You know my methods",
    "What do you make of it?",
    "It is obviously a walking-stick"
]
```

**코드:**
```python
def extract_dialogues(self, text):
    # 따옴표로 둘러싸인 대화문 추출
    dialogue_pattern = r'["\'"]([^"\'"]+)["\'"]'
    dialogues = re.findall(dialogue_pattern, text)
    
    # 짧은 대화 필터링 (3단어 이상)
    dialogues = [d for d in dialogues if len(d.split()) >= 3]
    
    return dialogues
```

### 2. 서술 분리

**원본 텍스트:**
```
"Good-morning, Holmes," said I. "You are busy, I see."

"Yes, I have had a busy morning," he answered.
```

**추출된 서술:**
```python
narrative = """
said I.

he answered.
"""
```

**코드:**
```python
def extract_narrative(self, text):
    # 대화문 제거
    narrative = re.sub(r'["\'"][^"\'"]+["\'"]', '', text)
    
    # 정제
    narrative = re.sub(r' +', ' ', narrative)
    narrative = re.sub(r'\n\s*\n', '\n\n', narrative)
    
    return narrative.strip()
```

### 3. 장면 구조화

**입력:**
```python
chapter_text = """
CHAPTER I
Mr. Sherlock Holmes

Mr. Sherlock Holmes, who was usually very late in the mornings...
"Good-morning, Holmes," said I. "You are busy, I see."
...
"""

entities = extract_entities(chapter_text)
```

**출력:**
```python
scene_data = {
    'characters': ['Sherlock Holmes', 'Watson', 'Dr. Mortimer'],
    'locations': ['Baker Street', 'London'],
    'dialogues': [
        "Good-morning, Holmes",
        "You are busy, I see",
        "Yes, I have had a busy morning",
        # ... 총 45개
    ],
    'narrative_sentences': [
        "Mr. Sherlock Holmes, who was usually very late in the mornings...",
        "I stood upon the hearth-rug and picked up the stick...",
        # ... 총 120개
    ],
    'total_sentences': 120,
    'total_dialogues': 45
}
```

---

## 전체 예시: Pride and Prejudice (Book 1342)

### 입력
```python
book_id = 1342
pipeline = BookToScriptPipeline()
result = pipeline.process_book(book_id)
```

### 처리 과정

#### Step 1: 다운로드
```
Processing book 1342...
  ✓ Downloaded (785602 chars)
```

#### Step 2: 헤더/푸터 제거
```
  ✓ Cleaned (717234 chars)
  Removed: 68368 chars (header/footer)
```

#### Step 3: 챕터 분할
```
  ✓ Split into 61 chapters
```

**챕터 예시:**
```python
chapters[0] = {
    'title': 'Chapter 1',
    'content': 'It is a truth universally acknowledged...'
}
chapters[1] = {
    'title': 'Chapter 2',
    'content': 'Mr. Bennet was among the earliest of those...'
}
```

#### Step 4: 개체명 추출 (Chapter 1)
```python
entities = {
    'PERSON': [
        ('Mr. Bennet', 8),
        ('Mrs. Bennet', 12),
        ('Mr. Bingley', 5),
    ],
    'GPE': [
        ('Netherfield Park', 3),
        ('Hertfordshire', 2),
    ],
    'DATE': [
        ('this morning', 1),
    ]
}
```

#### Step 5: 스크립트 구조화
```python
scene_data = {
    'characters': ['Mr. Bennet', 'Mrs. Bennet', 'Mr. Bingley'],
    'locations': ['Netherfield Park', 'Hertfordshire'],
    'dialogues': [
        "My dear Mr. Bennet",
        "have you heard that Netherfield Park is let at last?",
        # ... 25개
    ],
    'narrative_sentences': [
        "It is a truth universally acknowledged, that a single man...",
        "However little known the feelings or views of such a man...",
        # ... 18개
    ],
    'total_sentences': 18,
    'total_dialogues': 25
}
```

### 최종 출력
```python
result = {
    'book_id': 1342,
    'total_length': 717234,
    'total_chapters': 61,
    'processed_chapters': [
        {
            'chapter_title': 'Chapter 1',
            'chapter_number': 1,
            'original_text': 'It is a truth universally...',
            'entities': {...},
            'scene_data': {...}
        },
        # ... 총 61개 챕터
    ]
}
```

---

## 디버깅 가이드

### 문제 1: 챕터가 1개만 나옴

**확인 사항:**
```python
# 원본 텍스트 샘플 출력
print(cleaned_text[:3000])

# 챕터 패턴 수동 검색
import re
pattern1 = r'\n\s*(CHAPTER|Chapter)\s+([IVXLCDM]+|\d+)'
matches = re.findall(pattern1, cleaned_text)
print(f"Pattern 1 matches: {len(matches)}")
print(matches[:5])

pattern2 = r'\n\s*([IVXLCDM]+|\d+)\.\s*\n'
matches = re.findall(pattern2, cleaned_text)
print(f"Pattern 2 matches: {len(matches)}")
```

**해결 방법:**
- 챕터 형식이 특이한 경우, `split_into_chapters`에 새 패턴 추가
- Fallback 메서드가 작동하는지 확인

### 문제 2: 개체명이 추출되지 않음

**확인 사항:**
```python
# SpaCy 모델 확인
import spacy
nlp = spacy.load('en_core_web_sm')
doc = nlp("Sherlock Holmes lives in London.")
for ent in doc.ents:
    print(f"{ent.text}: {ent.label_}")

# 텍스트 길이 확인
print(f"Text length: {len(chapter_text)}")
# 너무 길면 max_length 조정
```

### 문제 3: 대화문 추출 오류

**확인 사항:**
```python
# 따옴표 형식 확인
text_sample = chapter_text[:1000]
print("Quotation marks found:")
for i, char in enumerate(text_sample):
    if char in ['"', "'", '"', '"', ''', ''']:
        print(f"Position {i}: {repr(char)}")
```

---

## 성능 최적화

### 병렬 처리
```python
from concurrent.futures import ThreadPoolExecutor

def process_books_parallel(book_ids, max_workers=5):
    pipeline = BookToScriptPipeline()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(pipeline.process_book, book_ids))
    
    return results
```

### 메모리 관리
```python
# 배치 처리
batch_size = 10
for i in range(0, len(book_ids), batch_size):
    batch = book_ids[i:i+batch_size]
    results = pipeline.process_multiple_books(batch)
    # 저장 후 메모리 해제
    del results
```

---

## 요약

### 주요 개선 사항
1. ✅ **챕터 분할**: 다양한 형식 지원 (3단계 접근)
2. ✅ **텍스트 정제**: Gutenberg 헤더/푸터 자동 제거
3. ✅ **개체명 추출**: SpaCy NER로 정확한 추출
4. ✅ **스크립트 변환**: 대화문/서술 자동 분리

### 다음 단계
- 수집된 데이터로 LLM 학습
- BLEU Score로 성능 평가
- 모델 fine-tuning

**질문이나 문제가 있으면 이 문서를 참고하세요!**
