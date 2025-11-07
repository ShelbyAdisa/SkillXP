import os
import json
import google.generativeai as genai
from django.conf import settings
from django.utils import timezone
from .models import AIModelConfig, AIRequestLog

class AIService:
    """
    Main AI service class with Google Gemini API integration.
    """
    
    @staticmethod
    def get_model_config(model_type):
        """Get active model configuration for a specific type"""
        try:
            return AIModelConfig.objects.get(model_type=model_type, is_active=True)
        except AIModelConfig.DoesNotExist:
            return None
    
    @staticmethod
    def log_request(model_config, requesting_user, target_app, prompt, response=None, 
                   input_tokens=0, output_tokens=0, cost=0.0, latency=0, 
                   was_successful=True, error_message=None):
        """Log AI request for auditing and analytics"""
        return AIRequestLog.objects.create(
            model_config=model_config,
            user=requesting_user,
            target_app=target_app,
            prompt_text=prompt,
            response_text=response,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            latency_ms=latency,
            was_successful=was_successful,
            error_message=error_message
        )
    
    @staticmethod
    def call_gemini_api(model_config, prompt, requesting_user=None, target_app='SOCIAL'):
        """Call Google Gemini API"""
        try:
            api_key = os.getenv(model_config.api_key_env)
            if not api_key:
                raise ValueError(f"API key not found for environment variable: {model_config.api_key_env}")
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('models/gemini-2.0-flash')
            
            start_time = timezone.now()
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=model_config.temperature,
                    max_output_tokens=model_config.max_tokens
                )
            )
            end_time = timezone.now()
            
            latency = (end_time - start_time).total_seconds() * 1000
            
            result = {
                'text': response.text,
                'latency_ms': latency
            }
            
            # Log the request
            AIService.log_request(
                model_config=model_config,
                requesting_user=requesting_user,
                target_app=target_app,
                prompt=prompt,
                response=response.text,
                input_tokens=len(prompt),
                output_tokens=len(response.text),
                latency=latency,
                cost=0.0,  
                was_successful=True
            )
            
            return result
            
        except Exception as e:
            AIService.log_request(
                model_config=model_config,
                requesting_user=requesting_user,
                target_app=target_app,
                prompt=prompt,
                error_message=str(e),
                was_successful=False
            )
            return {'error': str(e)}
    
    @staticmethod
    def call_external_api(model_config, prompt, requesting_user=None, target_app='SOCIAL'):
        """Route to the appropriate API - currently only Gemini"""
        return AIService.call_gemini_api(model_config, prompt, requesting_user, target_app)
    
    @staticmethod
    def parse_json_response(api_response):
        """Parse API response text into JSON"""
        try:
            if 'error' in api_response:
                return api_response
            
            text = api_response.get('text', '')
            # Try to extract JSON from response text
            if '{' in text and '}' in text:
                start = text.find('{')
                end = text.rfind('}') + 1
                json_str = text[start:end]
                return json.loads(json_str)
            else:
                return {'raw_response': text}
        except json.JSONDecodeError:
            return {'raw_response': api_response.get('text', '')}
    
    @staticmethod
    def analyze_toxicity(text, requesting_user=None):
        """Analyze text for toxic content using Gemini"""
        model_config = AIService.get_model_config('TOXICITY')
        if not model_config:
            return {'error': 'No active toxicity model configured'}
        
        prompt = f"""
        Analyze this text for toxic, harmful, or inappropriate content. 
        Return ONLY a valid JSON object with these exact fields:
        - toxicity_score: number between 0 and 1
        - is_toxic: boolean
        - categories: array of strings (harassment, hate_speech, violence, etc.)
        - confidence: number between 0 and 1
        - explanation: brief explanation of the analysis
        
        Text to analyze: "{text}"
        """
        
        api_response = AIService.call_external_api(
            model_config=model_config,
            prompt=prompt,
            requesting_user=requesting_user,
            target_app='SOCIAL'
        )
        
        return AIService.parse_json_response(api_response)
    
    @staticmethod
    def analyze_sentiment(text, requesting_user=None):
        """Analyze text sentiment using Gemini"""
        model_config = AIService.get_model_config('NLP')
        if not model_config:
            return {'error': 'No active NLP model configured'}
        
        prompt = f"""
        Analyze the sentiment and emotional tone of this text.
        Return ONLY a valid JSON object with these exact fields:
        - sentiment_score: number from -1 (very negative) to 1 (very positive)
        - primary_emotion: string (happy, sad, angry, anxious, neutral, etc.)
        - urgency_level: string (low, medium, high)
        - needs_support: boolean
        - confidence: number between 0 and 1
        
        Text: "{text}"
        """
        
        api_response = AIService.call_external_api(
            model_config=model_config,
            prompt=prompt,
            requesting_user=requesting_user,
            target_app='WELLBEING'
        )
        
        return AIService.parse_json_response(api_response)
    
    @staticmethod
    def generate_recommendations(user_context, content_type, requesting_user=None):
        """Generate personalized recommendations using Gemini"""
        model_config = AIService.get_model_config('RECOMMENDATION')
        if not model_config:
            return {'error': 'No active recommendation model configured'}
        
        prompt = f"""
        Generate 3-5 personalized recommendations based on the user context and content type.
        Return ONLY a valid JSON object with these exact fields:
        - recommendations: array of strings (the recommendation texts)
        - reasoning: brief explanation of why these were chosen
        - confidence: number between 0 and 1
        
        User Context: {user_context}
        Content Type: {content_type}
        """
        
        api_response = AIService.call_external_api(
            model_config=model_config,
            prompt=prompt,
            requesting_user=requesting_user,
            target_app='ELIBRARY'
        )
        
        return AIService.parse_json_response(api_response)
    
    @staticmethod
    def summarize_content(text, max_length=200, requesting_user=None):
        """Summarize content using Gemini"""
        model_config = AIService.get_model_config('SUMMARIZATION')
        if not model_config:
            return {'error': 'No active summarization model configured'}
        
        prompt = f"""
        Summarize the following text in about {max_length} words, keeping the key information and main points.
        Return ONLY a valid JSON object with these exact fields:
        - summary: the summarized text
        - key_points: array of strings (3-5 main points)
        - reading_time_minutes: estimated reading time
        
        Text to summarize: "{text}"
        """
        
        api_response = AIService.call_external_api(
            model_config=model_config,
            prompt=prompt,
            requesting_user=requesting_user,
            target_app='ELIBRARY'
        )
        
        return AIService.parse_json_response(api_response)
    
    @staticmethod
    def answer_question(question, context, requesting_user=None):
        """Answer questions based on context using Gemini"""
        model_config = AIService.get_model_config('QNA')
        if not model_config:
            return {'error': 'No active Q&A model configured'}
        
        prompt = f"""
        Based on the provided context, answer the question clearly and helpfully.
        Return ONLY a valid JSON object with these exact fields:
        - answer: the direct answer to the question
        - confidence: number between 0 and 1
        - sources: array of strings (key sources from the context)
        - explanation: brief explanation of how the answer was derived
        
        Context: "{context}"
        Question: "{question}"
        """
        
        api_response = AIService.call_external_api(
            model_config=model_config,
            prompt=prompt,
            requesting_user=requesting_user,
            target_app='ELIBRARY'
        )
        
        return AIService.parse_json_response(api_response)
    
    @staticmethod
    def detect_crisis_indicators(text, requesting_user=None):
        """Detect crisis indicators in text using Gemini"""
        model_config = AIService.get_model_config('NLP')
        if not model_config:
            return {'error': 'No active NLP model configured'}
        
        prompt = f"""
        Analyze this text for crisis indicators, self-harm mentions, or urgent mental health needs.
        Return ONLY a valid JSON object with these exact fields:
        - crisis_level: string (none, low, medium, high, critical)
        - indicators: array of strings (detected crisis signs)
        - immediate_action_required: boolean
        - recommended_response: string (suggested action)
        - confidence: number between 0 and 1
        
        Text: "{text}"
        """
        
        api_response = AIService.call_external_api(
            model_config=model_config,
            prompt=prompt,
            requesting_user=requesting_user,
            target_app='WELLBEING'
        )
        
        return AIService.parse_json_response(api_response)

    # CLASSROOM-SPECIFIC AI METHODS
    @staticmethod
    def analyze_assignment_quality(assignment_title, assignment_description, rubric, requesting_user=None):
        """AI analysis of assignment quality and educational value"""
        model_config = AIService.get_model_config('NLP')
        if not model_config:
            return {'error': 'No active NLP model configured'}
        
        prompt = f"""
        Analyze this classroom assignment for educational quality, clarity, and effectiveness.
        Return ONLY a valid JSON object with these exact fields:
        - clarity_score: number between 0-1 (how clear the assignment is)
        - difficulty_level: string (easy, medium, hard, advanced)
        - alignment_score: number 0-1 (alignment with educational standards)
        - suggested_improvements: array of strings
        - time_estimate_minutes: estimated student completion time
        - confidence: number between 0-1
        
        Assignment Title: {assignment_title}
        Assignment Description: {assignment_description}
        Rubric: {rubric}
        """
        
        api_response = AIService.call_external_api(
            model_config=model_config,
            prompt=prompt,
            requesting_user=requesting_user,
            target_app='CLASSROOM'
        )
        
        return AIService.parse_json_response(api_response)

    @staticmethod
    def provide_submission_feedback(submission_content, assignment_rubric, requesting_user=None):
        """AI-generated feedback for student submissions"""
        model_config = AIService.get_model_config('NLP')
        if not model_config:
            return {'error': 'No active NLP model configured'}
        
        prompt = f"""
        Provide constructive feedback for this student submission based on the assignment rubric.
        Return ONLY a valid JSON object with these exact fields:
        - strengths: array of strings (what the student did well)
        - areas_for_improvement: array of strings (specific suggestions)
        - overall_feedback: string (general feedback)
        - estimated_grade_range: string (e.g., "B+ to A-")
        - confidence: number between 0-1
        
        Student Submission: {submission_content}
        Assignment Rubric: {assignment_rubric}
        """
        
        api_response = AIService.call_external_api(
            model_config=model_config,
            prompt=prompt,
            requesting_user=requesting_user,
            target_app='CLASSROOM'
        )
        
        return AIService.parse_json_response(api_response)

    @staticmethod
    def detect_plagiarism_risk(submission_content, assignment_context, requesting_user=None):
        """AI analysis of plagiarism risk and originality"""
        model_config = AIService.get_model_config('NLP')
        if not model_config:
            return {'error': 'No active NLP model configured'}
        
        prompt = f"""
        Analyze this student submission for potential plagiarism risk and originality.
        Return ONLY a valid JSON object with these exact fields:
        - originality_score: number between 0-1 (1 = highly original)
        - plagiarism_risk: string (low, medium, high)
        - flagged_sections: array of strings (sections that seem unoriginal)
        - recommendations: array of strings (suggestions for verification)
        - confidence: number between 0-1
        
        Submission Content: {submission_content}
        Assignment Context: {assignment_context}
        """
        
        api_response = AIService.call_external_api(
            model_config=model_config,
            prompt=prompt,
            requesting_user=requesting_user,
            target_app='CLASSROOM'
        )
        
        return AIService.parse_json_response(api_response)

    @staticmethod
    def generate_quiz_questions(topic, difficulty='medium', count=5, requesting_user=None):
        """AI-generated quiz questions for any topic"""
        model_config = AIService.get_model_config('QNA')
        if not model_config:
            return {'error': 'No active Q&A model configured'}
        
        prompt = f"""
        Generate {count} {difficulty}-level quiz questions about {topic}.
        Return ONLY a valid JSON object with these exact fields:
        - questions: array of objects, each with:
          * question: string
          * options: array of 4 strings
          * correct_answer: string (the correct option)
          * explanation: string
        - topic_coverage: array of strings (subtopics covered)
        - difficulty_analysis: string (analysis of question difficulty)
        
        Topic: {topic}
        Difficulty: {difficulty}
        Number of Questions: {count}
        """
        
        api_response = AIService.call_external_api(
            model_config=model_config,
            prompt=prompt,
            requesting_user=requesting_user,
            target_app='CLASSROOM'
        )
        
        return AIService.parse_json_response(api_response)

    @staticmethod
    def analyze_student_engagement(student_data, activity_logs, requesting_user=None):
        """AI analysis of student engagement patterns"""
        model_config = AIService.get_model_config('NLP')
        if not model_config:
            return {'error': 'No active NLP model configured'}
        
        prompt = f"""
        Analyze this student's engagement patterns and provide insights.
        Return ONLY a valid JSON object with these exact fields:
        - engagement_level: string (low, medium, high, exceptional)
        - risk_factors: array of strings (potential concerns)
        - strengths: array of strings (positive engagement patterns)
        - recommendations: array of strings (suggestions for improvement)
        - predicted_performance: string (below, meeting, exceeding expectations)
        - confidence: number between 0-1
        
        Student Data: {student_data}
        Activity Logs: {activity_logs}
        """
        
        api_response = AIService.call_external_api(
            model_config=model_config,
            prompt=prompt,
            requesting_user=requesting_user,
            target_app='CLASSROOM'
        )
        
        return AIService.parse_json_response(api_response)