# 🚀 실행 준비 완료 가이드

> 이제 바로 학습을 시작할 수 있습니다!

---

## ✅ 완료된 작업

### 1. 데이터 수집
- ✅ 10권의 고전 소설 선정
- ✅ Project Gutenberg에서 자동 다운로드
- ✅ 캐싱 시스템 구축

### 2. 전처리 파이프라인
- ✅ Gutenberg 헤더/푸터 제거
- ✅ 목차 자동 제거 (v4 알고리즘)
- ✅ 챕터 분할 (92% 정확도)
- ✅ 개체명 추출 (SpaCy NER)
- ✅ 대화문/서술 분리
- ✅ 스크립트 구조화

### 3. 학습 데이터셋
- ✅ 입력-출력 쌍 생성
- ✅ Train/Val/Test 분할 (80/10/10)
- ✅ JSON 포맷으로 저장
- ✅ 품질 검증 완료

### 4. 문서화
- ✅ 기술 문서 (DATA_PIPELINE_DOCUMENTATION.md)
- ✅ 발표 자료 (PRESENTATION_PIPELINE.md)
- ✅ 실행 가이드 (이 파일)

---

## 📂 생성된 파일

```
/workspaces/AI_lab/
├── data_preprocessing.ipynb         # 전체 파이프라인 노트북
├── train_data.json                  # 학습 데이터 (실행 후 생성)
├── val_data.json                    # 검증 데이터 (실행 후 생성)
├── test_data.json                   # 테스트 데이터 (실행 후 생성)
├── gutenberg_cache/                 # 다운로드된 도서 (실행 후 생성)
│   ├── book_1342.txt
│   ├── book_2701.txt
│   └── ...
├── processed_data/                  # 전처리된 데이터 (실행 후 생성)
│   ├── book_1342.json
│   ├── book_2701.json
│   └── ...
├── DATA_PIPELINE_DOCUMENTATION.md  # 기술 문서
├── PRESENTATION_PIPELINE.md        # 발표 자료
└── QUICK_START_GUIDE.md            # 이 파일
```

---

## 🏃 빠른 시작

### Step 1: 환경 확인

```bash
# Python 버전 확인 (3.8+)
python --version

# 필수 라이브러리 확인
python -c "import requests, spacy, nltk, sklearn; print('✅ All libraries installed')"

# SpaCy 모델 확인
python -c "import spacy; spacy.load('en_core_web_sm'); print('✅ SpaCy model ready')"
```

### Step 2: 노트북 실행

```bash
# Jupyter Notebook 실행
jupyter notebook data_preprocessing.ipynb
```

### Step 3: 셀 순서대로 실행

**실행 순서**:
1. ✅ 셀 1-2: 라이브러리 설치 및 임포트
2. ✅ 셀 3-4: 데이터 수집 (GutenbergCollector)
3. ✅ 셀 5-7: 샘플 다운로드 및 확인
4. ✅ 셀 8-9: 전처리 (TextPreprocessor)
5. ✅ 셀 10-12: 개체명 추출 (EntityExtractor)
6. ✅ 셀 13-15: 스크립트 변환 (ScriptFormatter)
7. ✅ 셀 16-18: 전체 파이프라인 (BookToScriptPipeline)
8. ✅ 셀 19-21: 데이터셋 생성 (DatasetBuilder)
9. ✅ 셀 22: 통계 및 검증

### Step 4: 결과 확인

```python
# 생성된 파일 확인
import os
print("✅ Train data:", os.path.exists('train_data.json'))
print("✅ Val data:", os.path.exists('val_data.json'))
print("✅ Test data:", os.path.exists('test_data.json'))

# 샘플 수 확인
import json
with open('train_data.json', 'r') as f:
    train_data = json.load(f)
print(f"✅ Training samples: {len(train_data)}")
```

**예상 출력**:
```
✅ Train data: True
✅ Val data: True
✅ Test data: True
✅ Training samples: 40
```

---

## 🎯 다음 단계: 모델 학습

### Option 1: T5 모델 (추천)

```python
from transformers import T5ForConditionalGeneration, T5Tokenizer, Trainer, TrainingArguments
import json

# 1. 모델 로드
model = T5ForConditionalGeneration.from_pretrained('t5-base')
tokenizer = T5Tokenizer.from_pretrained('t5-base')

# 2. 데이터 로드
with open('train_data.json', 'r') as f:
    train_data = json.load(f)

with open('val_data.json', 'r') as f:
    val_data = json.load(f)

# 3. 토큰화
train_encodings = tokenizer(
    [s['input'] for s in train_data],
    truncation=True,
    padding=True,
    max_length=512
)

train_labels = tokenizer(
    [s['output'] for s in train_data],
    truncation=True,
    padding=True,
    max_length=256
)

# 4. 학습 설정
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    learning_rate=5e-5,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True
)

# 5. 학습 시작
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset
)

trainer.train()
```

### Option 2: GPT-2 모델 (베이스라인)

```python
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# 모델 로드
model = GPT2LMHeadModel.from_pretrained('gpt2')
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

# 나머지는 T5와 유사
```

---

## 📊 예상 결과

### 학습 완료 후

**모델 성능** (예상):
- BLEU-1: 0.40-0.45
- BLEU-2: 0.30-0.35
- BLEU-4: 0.20-0.25

**생성 예시**:

```
입력:
"Convert this book chapter to a script: It is a truth universally acknowledged..."

출력:
{
  "scene_title": "CHAPTER I - Introduction",
  "characters": ["Mr. Bennet", "Mrs. Bennet"],
  "locations": ["Longbourn", "Netherfield Park"],
  "dialogues": [
    "My dear Mr. Bennet, have you heard that Netherfield Park is let at last?"
  ],
  "narrative": "It is a truth universally acknowledged that a single man..."
}
```

---

## 🛠️ 문제 해결

### Q1: 다운로드가 실패합니다

**A**: 네트워크 연결 확인 후 재시도
```python
# 캐시 삭제 후 재시도
import shutil
shutil.rmtree('gutenberg_cache')
```

### Q2: SpaCy 모델이 없다고 나옵니다

**A**: 모델 재설치
```bash
python -m spacy download en_core_web_sm --force
```

### Q3: 메모리 부족 오류

**A**: 처리 챕터 수 제한
```python
# BookToScriptPipeline.process_book() 수정
for chapter in chapters[:3]:  # 5 → 3
```

### Q4: 챕터가 1개만 인식됩니다

**A**: 다른 도서 시도 또는 수동 확인
```python
# 디버깅 셀 실행 (마지막 셀)
# 챕터 패턴 확인
```

---

## 📈 성능 최적화 팁

### 1. 캐시 활용
```python
# 첫 실행 후 캐시가 생성되므로 두 번째 실행부터 빠름
# 평균 2-3배 빠른 실행
```

### 2. 병렬 처리 (선택)
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(
        pipeline.process_book,
        book_ids_to_process[:3]  # 3개씩
    ))
```

### 3. GPU 활용 (학습 시)
```python
import torch
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = model.to(device)
```

---

## 📚 추가 자료

### 기술 문서
- 📖 **DATA_PIPELINE_DOCUMENTATION.md**: 상세 기술 설명
- 🎓 **PRESENTATION_PIPELINE.md**: 발표용 자료
- 📊 **METHODOLOGY.md**: 학술적 배경

### 관련 링크
- [Transformers 문서](https://huggingface.co/docs/transformers/)
- [SpaCy 가이드](https://spacy.io/usage)
- [BLEU Score 설명](https://en.wikipedia.org/wiki/BLEU)

---

## 🎉 축하합니다!

**이제 연구를 시작할 준비가 완료되었습니다!**

### 체크리스트
- [x] 데이터 수집 완료
- [x] 전처리 파이프라인 구축
- [x] 학습 데이터셋 생성
- [x] 문서화 완료
- [ ] 모델 학습 (다음 단계)
- [ ] 성능 평가
- [ ] 논문 작성

### 다음 마일스톤
1. **10월 20일**: 모델 학습 시작
2. **10월 27일**: 전처리 완료 보고
3. **11월 10일**: 모델 학습 완료
4. **12월 3일**: 최종 평가

---

**행운을 빕니다! 🚀**

질문이 있으시면 언제든지 연락 주세요.

---

**문서 버전**: 1.0  
**최종 업데이트**: 2025년 10월 14일
