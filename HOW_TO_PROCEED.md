# 다음 주까지 데이터 전처리 진행 방안

## 질문에 대한 답변
> "교수님의 면담을 토대로, 다음 주까지 데이터 전처리에 대해 진행해야 해 어떻게 진행해야할까?"

## 📋 요약 답변

교수님의 Comment-2를 기반으로 **병렬 작업 방식**을 추천드립니다:

1. **데이터 수집 담당자 (1명)**: 도서 다운로드에 집중
2. **프레임워크 담당자 (나머지)**: 전처리 파이프라인 최적화 및 검증

이미 모든 필요한 코드와 가이드가 `data_preprocessing.ipynb`에 준비되어 있습니다.

## 🎯 구체적인 실행 계획 (7일)

### Day 1-2: 준비 및 시작 (10월 12-13일)

#### 전체 팀원
```bash
# 1. 환경 설정
pip install torch transformers datasets nltk spacy beautifulsoup4 requests scikit-learn
python -m spacy download en_core_web_sm

# 2. 노트북 실행 확인
jupyter notebook data_preprocessing.ipynb
```

#### 데이터 수집 담당
```python
# data_preprocessing.ipynb에서 실행
collector = GutenbergCollector()

# 목표 도서 ID 리스트 (50권)
book_ids = collector.get_popular_books(limit=50)

# 매일 10-15권씩 다운로드
for book_id in book_ids[:15]:
    print(f"Downloading book {book_id}...")
    text = collector.download_book(book_id)
    if text:
        # 저장
        with open(f'raw_data/book_{book_id}.txt', 'w') as f:
            f.write(text)
    time.sleep(1)  # 서버 부하 방지
```

#### 프레임워크 담당
```python
# 샘플 데이터로 파이프라인 검증
pipeline = BookToScriptPipeline()

# 테스트 (Pride and Prejudice)
result = pipeline.process_book(1342)

# 결과 확인
print(f"Chapters: {result['total_chapters']}")
print(f"First chapter entities: {result['processed_chapters'][0]['entities']}")
```

### Day 3-4: 대규모 처리 (10월 14-15일)

#### 데이터 수집 담당
```python
# 계속 수집 (누적 30-40권 목표)
# 다양한 장르 확보
fiction_ids = [1342, 84, 98, 1661, 2701, ...]
drama_ids = [...]
mystery_ids = [...]

all_ids = fiction_ids + drama_ids + mystery_ids
```

#### 프레임워크 담당
```python
# 수집된 도서 전처리 시작
import os
import glob

# raw_data 폴더의 모든 txt 파일 처리
raw_files = glob.glob('raw_data/*.txt')
book_ids = [int(f.split('_')[1].split('.')[0]) for f in raw_files]

# 배치 처리
results = pipeline.process_multiple_books(
    book_ids,
    output_dir='./processed_data'
)

# 진행 상황 저장
import json
with open('processing_log.json', 'w') as f:
    json.dump({
        'date': '2025-10-15',
        'processed_books': len(results),
        'total_chapters': sum(r['total_chapters'] for r in results)
    }, f)
```

### Day 5: 품질 검증 (10월 16일)

#### 전체 팀원 협업
```python
# 1. 데이터 통계 분석
stats = {
    'total_books': 0,
    'total_chapters': 0,
    'total_characters': 0,
    'avg_chapter_length': 0,
    'books_with_errors': []
}

for result in results:
    stats['total_books'] += 1
    stats['total_chapters'] += result['total_chapters']
    stats['total_characters'] += result['total_length']
    
    # 에러 체크
    if result['total_chapters'] == 0:
        stats['books_with_errors'].append(result['book_id'])

stats['avg_chapter_length'] = stats['total_characters'] / stats['total_chapters']

print(json.dumps(stats, indent=2))

# 2. 결측치 확인
missing_data = []
for result in results:
    for chapter in result['processed_chapters']:
        if not chapter['entities']['PERSON']:
            missing_data.append({
                'book_id': result['book_id'],
                'chapter': chapter['chapter_number'],
                'issue': 'No characters found'
            })

print(f"Missing data issues: {len(missing_data)}")

# 3. 샘플 데이터 수동 검증
import random
sample = random.choice(results)
print(f"\n=== Sample Book {sample['book_id']} ===")
print(f"Chapters: {sample['total_chapters']}")
sample_chapter = sample['processed_chapters'][0]
print(f"Sample chapter: {sample_chapter['chapter_title']}")
print(f"Characters: {[c for c, _ in sample_chapter['entities']['PERSON'][:5]]}")
print(f"Locations: {[l for l, _ in (sample_chapter['entities']['GPE'] + sample_chapter['entities']['LOC'])[:3]]}")
```

### Day 6: 학습 데이터 구축 (10월 17일)

```python
# 1. 학습 데이터 포맷 정의
training_dataset = []

for result in results:
    for chapter in result['processed_chapters']:
        # 입력: 원본 챕터 텍스트
        input_text = chapter['original_text']
        
        # 출력: 구조화된 스크립트 정보
        output_script = {
            'scene': chapter['chapter_title'],
            'characters': [c for c, _ in chapter['entities']['PERSON'][:10]],
            'locations': [l for l, _ in (chapter['entities']['GPE'] + chapter['entities']['LOC'])[:5]],
            'key_dialogues': chapter['scene_data']['dialogues'][:20],
            'narrative_summary': ' '.join(chapter['scene_data']['narrative_sentences'][:10])
        }
        
        training_dataset.append({
            'input': input_text,
            'output': output_script,
            'metadata': {
                'book_id': result['book_id'],
                'chapter_number': chapter['chapter_number']
            }
        })

print(f"Training dataset size: {len(training_dataset)} samples")

# 2. 데이터셋 분할
from sklearn.model_selection import train_test_split

train_data, temp_data = train_test_split(training_dataset, test_size=0.2, random_state=42)
val_data, test_data = train_test_split(temp_data, test_size=0.5, random_state=42)

print(f"Train: {len(train_data)}, Val: {len(val_data)}, Test: {len(test_data)}")

# 3. 저장
import json
with open('train_data.json', 'w') as f:
    json.dump(train_data, f, ensure_ascii=False, indent=2)
with open('val_data.json', 'w') as f:
    json.dump(val_data, f, ensure_ascii=False, indent=2)
with open('test_data.json', 'w') as f:
    json.dump(test_data, f, ensure_ascii=False, indent=2)
```

### Day 7: 문서화 및 정리 (10월 18일)

```python
# 최종 보고서 생성
final_report = {
    'project': 'Book to Script Conversion - Data Preprocessing',
    'date': '2025-10-18',
    'deadline': '2025-10-27',
    'status': 'COMPLETED',
    
    'data_collection': {
        'total_books': stats['total_books'],
        'sources': ['Project Gutenberg'],
        'genres': {
            'fiction': 30,
            'drama': 10,
            'mystery': 10
        }
    },
    
    'data_preprocessing': {
        'total_chapters': stats['total_chapters'],
        'total_characters': stats['total_characters'],
        'avg_chapter_length': stats['avg_chapter_length'],
        'preprocessing_steps': [
            'Gutenberg header/footer removal',
            'Text cleaning',
            'Chapter segmentation',
            'Entity extraction (PERSON, GPE, LOC, DATE)',
            'Dialogue extraction',
            'Scene structuring'
        ]
    },
    
    'dataset': {
        'train_samples': len(train_data),
        'val_samples': len(val_data),
        'test_samples': len(test_data),
        'total_samples': len(training_dataset)
    },
    
    'next_steps': [
        'Model selection (T5, BART, GPT-2)',
        'Fine-tuning strategy',
        'Training setup',
        'Evaluation metrics implementation'
    ],
    
    'issues_found': stats['books_with_errors'],
    'issues_resolved': len(stats['books_with_errors']) - len(missing_data)
}

# 보고서 저장
with open('final_report.json', 'w') as f:
    json.dump(final_report, f, ensure_ascii=False, indent=2)

# 요약 출력
print("="*50)
print("데이터 전처리 완료 보고")
print("="*50)
print(f"📚 수집된 도서: {final_report['data_collection']['total_books']}권")
print(f"📖 처리된 챕터: {final_report['data_preprocessing']['total_chapters']}개")
print(f"📊 학습 데이터: {final_report['dataset']['total_samples']}개")
print(f"✅ 전처리 완료: {final_report['status']}")
print("="*50)
```

## 💡 핵심 포인트

### 1. 이미 준비된 것
✅ `data_preprocessing.ipynb` - 완전한 파이프라인  
✅ `DATA_PREPROCESSING_GUIDE.md` - 상세 가이드  
✅ `QUICK_START.md` - 빠른 시작 가이드  

### 2. 해야 할 것 (순서대로)
1. 노트북 열기: `data_preprocessing.ipynb`
2. 모든 셀 순서대로 실행
3. 도서 ID 리스트 확장 (50권 목표)
4. `pipeline.process_multiple_books()` 실행
5. 결과 검증 및 저장

### 3. 시간 배분
- **데이터 수집**: 40% (도서 다운로드)
- **전처리 실행**: 30% (파이프라인 실행)
- **품질 검증**: 20% (결과 확인)
- **문서화**: 10% (보고서 작성)

## 🚨 주의사항

### 반드시 지켜야 할 것
1. **매일 진행상황 저장**: 데이터 손실 방지
2. **정기 백업**: `raw_data/`, `processed_data/` 폴더
3. **에러 로깅**: 실패한 도서 ID 기록
4. **팀 커뮤니케이션**: 매일 오후 6시 진행 공유

### 문제 발생 시
```python
# 문제 상황 기록
error_log = {
    'date': '2025-10-XX',
    'error_type': 'Download failed',
    'book_id': 1234,
    'error_message': '...',
    'solution': 'Retried with longer timeout'
}
```

## 📊 예상 결과물 (10월 27일)

### 파일 구조
```
AI_lab/
├── data_preprocessing.ipynb          # 작업 노트북
├── raw_data/                          # 원본 도서 (50+ files)
│   ├── book_1342.txt
│   ├── book_84.txt
│   └── ...
├── processed_data/                    # 전처리된 데이터 (50+ files)
│   ├── book_1342.json
│   ├── book_84.json
│   └── ...
├── train_data.json                    # 학습 데이터 (80%)
├── val_data.json                      # 검증 데이터 (10%)
├── test_data.json                     # 테스트 데이터 (10%)
├── final_report.json                  # 최종 보고서
├── processing_log.json                # 처리 로그
└── progress_summary.json              # 진행 상황 요약
```

### 달성 목표
- ✅ 50권 이상 도서 수집
- ✅ 전체 도서 전처리 완료
- ✅ 학습 데이터셋 구축
- ✅ 데이터 품질 검증
- ✅ 다음 단계 준비 (모델링)

## 🎓 교수님 피드백 반영

### Comment-1: 성능 평가 우선순위
1. **BLEU** (필수) ✅ 이미 구현됨
2. **FVD** (선택) - 모델링 후 결정
3. **CLIPScore** (선택) - 여유 있을 때

### Comment-2: 병렬 작업
✅ 데이터 수집 + 프레임워크 셋업 동시 진행  
✅ 역할 분담 명확히  
✅ 매일 진행 상황 공유  

---

**시작하기**: `data_preprocessing.ipynb` 열고 첫 번째 셀부터 실행!

**질문/문제**: 팀 채팅방에 공유

**마감**: 2025년 10월 27일

**다음 단계**: 모델링 (10월 28일~)
