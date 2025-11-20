#!/usr/bin/env python3
"""
진행 상황 추적 도구 (Progress Tracker)

사용법:
    python track_progress.py --check          # 현재 진행 상황 확인
    python track_progress.py --add-book 1342  # 도서 처리 완료 기록
    python track_progress.py --report         # 일일 보고서 생성
"""

import json
import os
from datetime import datetime
from pathlib import Path

class ProgressTracker:
    def __init__(self, data_dir='./'):
        self.data_dir = Path(data_dir)
        self.progress_file = self.data_dir / 'progress_tracker.json'
        self.load_progress()
    
    def load_progress(self):
        """진행 상황 로드"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                self.progress = json.load(f)
        else:
            self.progress = {
                'start_date': datetime.now().strftime('%Y-%m-%d'),
                'deadline': '2025-10-27',
                'books': {
                    'collected': [],
                    'processed': [],
                    'failed': []
                },
                'daily_logs': []
            }
    
    def save_progress(self):
        """진행 상황 저장"""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)
    
    def add_collected_book(self, book_id):
        """수집 완료된 도서 추가"""
        if book_id not in self.progress['books']['collected']:
            self.progress['books']['collected'].append(book_id)
            self.save_progress()
            print(f"✓ Book {book_id} marked as collected")
    
    def add_processed_book(self, book_id):
        """전처리 완료된 도서 추가"""
        if book_id not in self.progress['books']['processed']:
            self.progress['books']['processed'].append(book_id)
            self.save_progress()
            print(f"✓ Book {book_id} marked as processed")
    
    def add_failed_book(self, book_id, reason=''):
        """실패한 도서 기록"""
        failure_record = {
            'book_id': book_id,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'reason': reason
        }
        self.progress['books']['failed'].append(failure_record)
        self.save_progress()
        print(f"✗ Book {book_id} marked as failed: {reason}")
    
    def add_daily_log(self, log_entry):
        """일일 로그 추가"""
        log = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'entry': log_entry
        }
        self.progress['daily_logs'].append(log)
        self.save_progress()
        print(f"✓ Log added: {log_entry}")
    
    def check_progress(self):
        """현재 진행 상황 확인"""
        collected = len(self.progress['books']['collected'])
        processed = len(self.progress['books']['processed'])
        failed = len(self.progress['books']['failed'])
        
        print("="*60)
        print("📊 현재 진행 상황")
        print("="*60)
        print(f"시작일: {self.progress['start_date']}")
        print(f"마감일: {self.progress['deadline']}")
        print()
        print(f"📚 수집된 도서: {collected}/50")
        print(f"   진행률: {self._progress_bar(collected, 50)}")
        print()
        print(f"⚙️  전처리 완료: {processed}/50")
        print(f"   진행률: {self._progress_bar(processed, 50)}")
        print()
        print(f"❌ 실패: {failed}건")
        print()
        
        # 최근 로그
        if self.progress['daily_logs']:
            print("📝 최근 활동:")
            for log in self.progress['daily_logs'][-3:]:
                print(f"   [{log['date']} {log['time']}] {log['entry']}")
        print("="*60)
    
    def _progress_bar(self, current, total, width=40):
        """진행률 바 생성"""
        filled = int(width * current / total)
        bar = '█' * filled + '░' * (width - filled)
        percentage = (current / total) * 100
        return f"[{bar}] {percentage:.1f}% ({current}/{total})"
    
    def generate_daily_report(self):
        """일일 보고서 생성"""
        today = datetime.now().strftime('%Y-%m-%d')
        collected = len(self.progress['books']['collected'])
        processed = len(self.progress['books']['processed'])
        
        report = f"""
# 일일 진행 보고서
날짜: {today}

## 📊 통계
- 수집된 도서: {collected}권
- 전처리 완료: {processed}권
- 실패: {len(self.progress['books']['failed'])}건

## 📈 진행률
- 수집: {(collected/50)*100:.1f}%
- 전처리: {(processed/50)*100:.1f}%

## 📝 오늘의 활동
"""
        
        # 오늘의 로그
        today_logs = [log for log in self.progress['daily_logs'] 
                      if log['date'] == today]
        
        if today_logs:
            for log in today_logs:
                report += f"- [{log['time']}] {log['entry']}\n"
        else:
            report += "- 기록된 활동 없음\n"
        
        # 다음 목표
        if collected < 50:
            remaining = 50 - collected
            report += f"\n## 🎯 다음 목표\n- 도서 {remaining}권 추가 수집 필요\n"
        
        if processed < collected:
            remaining = collected - processed
            report += f"- 수집된 도서 {remaining}권 전처리 필요\n"
        
        print(report)
        
        # 파일로 저장
        report_file = self.data_dir / f'daily_report_{today}.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✓ Report saved to: {report_file}")
    
    def scan_directories(self):
        """디렉토리를 스캔하여 자동으로 진행 상황 업데이트"""
        raw_data_dir = self.data_dir / 'raw_data'
        processed_data_dir = self.data_dir / 'processed_data'
        
        # 수집된 도서 스캔
        if raw_data_dir.exists():
            for file in raw_data_dir.glob('book_*.txt'):
                book_id = int(file.stem.split('_')[1])
                if book_id not in self.progress['books']['collected']:
                    self.progress['books']['collected'].append(book_id)
        
        # 전처리된 도서 스캔
        if processed_data_dir.exists():
            for file in processed_data_dir.glob('book_*.json'):
                book_id = int(file.stem.split('_')[1])
                if book_id not in self.progress['books']['processed']:
                    self.progress['books']['processed'].append(book_id)
        
        self.save_progress()
        print("✓ Directories scanned and progress updated")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='진행 상황 추적 도구')
    parser.add_argument('--check', action='store_true', 
                       help='현재 진행 상황 확인')
    parser.add_argument('--add-book', type=int, metavar='BOOK_ID',
                       help='도서 처리 완료 기록')
    parser.add_argument('--report', action='store_true',
                       help='일일 보고서 생성')
    parser.add_argument('--scan', action='store_true',
                       help='디렉토리 스캔하여 자동 업데이트')
    parser.add_argument('--log', type=str, metavar='MESSAGE',
                       help='로그 메시지 추가')
    
    args = parser.parse_args()
    tracker = ProgressTracker()
    
    if args.check:
        tracker.check_progress()
    elif args.add_book:
        tracker.add_collected_book(args.add_book)
        tracker.add_processed_book(args.add_book)
    elif args.report:
        tracker.generate_daily_report()
    elif args.scan:
        tracker.scan_directories()
        tracker.check_progress()
    elif args.log:
        tracker.add_daily_log(args.log)
    else:
        # 기본: 진행 상황 확인
        tracker.check_progress()


if __name__ == '__main__':
    main()
