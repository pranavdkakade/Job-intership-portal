"""
Management command to verify extracted questions from vector stores
"""
from django.core.management.base import BaseCommand
import pickle
from pathlib import Path
from django.conf import settings

class Command(BaseCommand):
    help = 'Verify extracted questions from vector stores'

    def add_arguments(self, parser):
        parser.add_argument(
            '--topic',
            type=str,
            choices=['sql', 'python', 'all'],
            default='all',
            help='Topic to verify (sql, python, or all)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=5,
            help='Number of questions to display per topic'
        )

    def handle(self, *args, **options):
        topic = options['topic']
        limit = options['limit']
        
        topics = ['sql', 'python'] if topic == 'all' else [topic]
        
        self.stdout.write("=" * 70)
        self.stdout.write(" Question Bank Verification")
        self.stdout.write("=" * 70)
        
        for t in topics:
            self.stdout.write(f"\n{'=' * 70}")
            self.stdout.write(f" {t.upper()} Questions")
            self.stdout.write(f"{'=' * 70}\n")
            
            vector_store_dir = Path(settings.MEDIA_ROOT) / 'vector_stores' / t
            questions_path = vector_store_dir / 'questions.pkl'
            
            if not questions_path.exists():
                self.stdout.write(self.style.ERROR(f"❌ No vector store found for {t}"))
                self.stdout.write("   Run: python manage.py build_question_banks\n")
                continue
            
            try:
                with open(questions_path, 'rb') as f:
                    questions = pickle.load(f)
                
                total = len(questions)
                self.stdout.write(f"Total Questions: {total}\n")
                
                display_count = min(limit, total)
                self.stdout.write(f"Showing first {display_count} questions:\n")
                
                for i, question in enumerate(questions[:display_count], 1):
                    self.stdout.write(f"\n--- Question {i} ---")
                    
                    # Truncate long questions for display
                    if len(question) > 200:
                        display_text = question[:200] + "..."
                    else:
                        display_text = question
                    
                    self.stdout.write(display_text)
                    
                    # Check if answer might be included
                    if any(marker in question.lower() for marker in ['answer:', 'a:', 'ans:', 'solution:']):
                        self.stdout.write(self.style.WARNING("⚠️  Possible answer detected in question!"))
                
                if total > display_count:
                    self.stdout.write(f"\n... and {total - display_count} more questions")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error loading {t}: {str(e)}"))
        
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write("Done!")
        self.stdout.write("=" * 70 + "\n")
