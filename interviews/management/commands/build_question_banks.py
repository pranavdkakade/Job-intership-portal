"""
Django management command to build question bank vector stores
Usage: python manage.py build_question_banks [--topic sql|python]
"""

from django.core.management.base import BaseCommand
from interviews.services.question_bank_processor import (
    QuestionBankProcessor, 
    initialize_all_topics
)


class Command(BaseCommand):
    help = 'Build FAISS vector stores from question bank PDFs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--topic',
            type=str,
            choices=['sql', 'python', 'all'],
            default='all',
            help='Topic to process (default: all)'
        )
        
        parser.add_argument(
            '--verify',
            action='store_true',
            help='Verify existing vector stores'
        )

    def handle(self, *args, **options):
        topic = options['topic']
        verify_only = options['verify']

        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('Question Bank Vector Store Builder'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))

        if verify_only:
            self.verify_stores(topic)
            return

        if topic == 'all':
            self.stdout.write("Building vector stores for ALL topics...\n")
            results = initialize_all_topics()
            
            self.stdout.write('\n' + '='*60)
            self.stdout.write(self.style.SUCCESS('Summary:'))
            self.stdout.write('='*60)
            
            for topic_name, result in results.items():
                if result['success']:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ {topic_name.upper()}: {result['count']} questions"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"❌ {topic_name.upper()}: {result['error']}"
                        )
                    )
        else:
            self.stdout.write(f"Building vector store for {topic.upper()}...\n")
            try:
                processor = QuestionBankProcessor(topic)
                count = processor.create_vector_store()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n✅ Successfully built {topic.upper()} vector store with {count} questions"
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"\n❌ Error building {topic.upper()} vector store: {e}"
                    )
                )

        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS('Done! You can now start Single Topic interviews.')
        )
        self.stdout.write('='*60 + '\n')

    def verify_stores(self, topic):
        """Verify existing vector stores"""
        self.stdout.write("Verifying vector stores...\n")
        
        topics_to_check = ['sql', 'python'] if topic == 'all' else [topic]
        
        for topic_name in topics_to_check:
            processor = QuestionBankProcessor(topic_name)
            info = processor.verify_vector_store()
            
            if info['exists']:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ {topic_name.upper()}: {info['total_questions']} questions, "
                        f"{info['dimensions']} dimensions"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"❌ {topic_name.upper()}: Not found or invalid - {info.get('error', 'Unknown error')}"
                    )
                )
