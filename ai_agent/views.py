import json
import os
import uuid
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Conversation, Message
from .services.agent_services import agent  # ← Updated import


def agent_interface(request):
    """Render the chat/voice interface"""
    return render(request, 'agents/interface.html')


@csrf_exempt
def chat_api(request):
    """Handle text chat messages"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        # Get conversation history
        conv, _ = Conversation.objects.get_or_create(session_id=session_id)
        history = [
            {'role': msg.role, 'content': msg.content}
            for msg in conv.messages.all()
        ]
        
        # Get AI response with tool calling
        response = agent.chat(user_message, history)
        
        # Save messages
        Message.objects.create(conversation=conv, role='user', content=user_message)
        Message.objects.create(conversation=conv, role='assistant', content=response['text'])
        
        return JsonResponse({
            'success': True,
            'response': response['text'],
            'session_id': session_id
        })
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({
            'error': str(e),
            'response': 'Sorry, I encountered an error. Please try again.'
        }, status=500)


@csrf_exempt
def voice_api(request):
    """Handle voice input and return voice response"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        audio_file = request.FILES.get('audio')
        if not audio_file:
            return JsonResponse({'error': 'No audio file'}, status=400)
        
        session_id = request.POST.get('session_id', str(uuid.uuid4()))
        
        # Save uploaded audio
        filename = f"input_{session_id}_{uuid.uuid4()}.webm"
        filepath = f"media/ai_agent/audio/input/{filename}"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'wb+') as dest:
            for chunk in audio_file.chunks():
                dest.write(chunk)
        
        # Get conversation history for voice context
        conv, _ = Conversation.objects.get_or_create(session_id=session_id)
        history = [
            {'role': msg.role, 'content': msg.content}
            for msg in conv.messages.all()
        ]
        
        # Process with Gemini agent (pass history)
        result = agent.process_voice(filepath, history)
        
        # Save conversation
        Message.objects.create(
            conversation=conv,
            role='user',
            content=result['user_text']
        )
        Message.objects.create(
            conversation=conv,
            role='assistant',
            content=result['ai_text']
        )
        
        return JsonResponse({
            'success': True,
            'user_text': result['user_text'],
            'ai_text': result['ai_text'],
            'audio_url': result['audio_url'],
            'session_id': session_id
        })
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)