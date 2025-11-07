from django.core.management.base import BaseCommand, CommandError
from ai_engine.services import generate_ai_response

class Command(BaseCommand):
    help = 'Tests the AI engine by sending a prompt to the Gemini API.'

    def add_arguments(self, parser):
        # This method defines the 'prompt' argument that accepts your question.
        parser.add_argument(
            'prompt', 
            type=str, 
            help='The question or prompt you want to ask the AI model.'
        )

    def handle(self, *args, **options):
        # Retrieves the text from the 'prompt' argument
        prompt = options['prompt']
        
        self.stdout.write(f"Sending prompt to AI model: '{prompt}'")
        self.stdout.write("-" * 50)
        
        # Calls the function that talks to the Gemini API
        response_text = generate_ai_response(prompt)
        
        self.stdout.write("AI Response:")
        self.stdout.write(self.style.SUCCESS(response_text))
        self.stdout.write("-" * 50)