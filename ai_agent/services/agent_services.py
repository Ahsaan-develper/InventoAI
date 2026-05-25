import os
import uuid
import logging
from django.conf import settings
import google.generativeai as genai
from .tools import ProductTools

# Suppress ALTS warning
logging.getLogger('google.api_core').setLevel(logging.ERROR)
os.environ['GRPC_VERBOSITY'] = 'ERROR'

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

# Lazy-load local Whisper model
_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
    return _whisper_model


class GeminiAgent:
    """AI Agent using Gemini 1.5 Flash with local Whisper STT"""
    
    SYSTEM_PROMPT = """You are InventoAI, a helpful store assistant. You help customers find products and answer questions about prices, availability, and details.

Rules:
- Always be friendly and concise
- When asked about a product, use the search_products tool
- If multiple products match, list them with prices and quantities
- If exact product found, give full details including price and available quantity
- If quantity is 0, clearly say the product is out of stock
- For voice responses, keep answers short and natural
- Always mention the price and quantity when discussing a product
- When asked about total products in store, use get_total_products_count tool
- When asked about total value of a product (price × quantity), use get_product_total_value tool
- Always show the calculation clearly: "Price $X × Quantity Y = Total $Z"""
    
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-lite",
            system_instruction=self.SYSTEM_PROMPT,
            tools=self._get_tools()
        )
    
    def _get_tools(self):
        return [
            genai.protos.Tool(
                function_declarations=[
                    genai.protos.FunctionDeclaration(
                        name="search_products",
                        description="Search for products by name or description keyword",
                        parameters=genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            properties={
                                "query": genai.protos.Schema(type=genai.protos.Type.STRING)
                            },
                            required=["query"]
                        )
                    ),
                    genai.protos.FunctionDeclaration(
                        name="get_product_details",
                        description="Get detailed info about a specific product by ID",
                        parameters=genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            properties={
                                "product_id": genai.protos.Schema(type=genai.protos.Type.INTEGER)
                            },
                            required=["product_id"]
                        )
                    ),
                    genai.protos.FunctionDeclaration(
                        name="get_all_products",
                        description="Get a list of all available products",
                        parameters=genai.protos.Schema(type=genai.protos.Type.OBJECT)
                    ),
                    genai.protos.FunctionDeclaration(
                        name="get_price_range",
                        description="Find products within a specific price range",
                        parameters=genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            properties={
                                "min_price": genai.protos.Schema(type=genai.protos.Type.NUMBER),
                                "max_price": genai.protos.Schema(type=genai.protos.Type.NUMBER)
                            },
                            required=["min_price", "max_price"]
                        )
                    ),
                    # ====== NEW TOOLS ======
                    genai.protos.FunctionDeclaration(
                        name="get_total_products_count",
                        description="Get total number of products in inventory, including in-stock and out-of-stock counts",
                        parameters=genai.protos.Schema(type=genai.protos.Type.OBJECT)
                    ),
                    genai.protos.FunctionDeclaration(
                        name="get_product_total_value",
                        description="Calculate total value of a product by multiplying price with quantity. Use when user asks 'total price of X' or 'how much is X worth'",
                        parameters=genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            properties={
                                "product_name": genai.protos.Schema(
                                    type=genai.protos.Type.STRING,
                                    description="Name of the product to calculate total value for"
                                )
                            },
                            required=["product_name"]
                        )
                    )
                ]
            )
        ]
    
    def _call_tool(self, tool_name: str, arguments: dict):
        if tool_name == "search_products":
            return ProductTools.search_products(**arguments)
        elif tool_name == "get_product_details":
            return ProductTools.get_product_details(**arguments)
        elif tool_name == "get_all_products":
            return ProductTools.get_all_products()
        elif tool_name == "get_price_range":
            return ProductTools.get_price_range(**arguments)
        elif tool_name == "get_total_products_count":
            return ProductTools.get_total_products_count()
        elif tool_name == "get_product_total_value":
            return ProductTools.get_product_total_value(**arguments)
        return {"error": "Unknown tool"}
    
    def _safe_extract_text(self, response):
        if not response.candidates:
            return "I'm not sure how to help with that."
        
        candidate = response.candidates[0]
        if not candidate.content or not candidate.content.parts:
            return "I'm not sure how to help with that."
        
        part = candidate.content.parts[0]
        
        if hasattr(part, 'function_call') and part.function_call:
            return "Let me check that for you."
        
        if hasattr(part, 'text') and part.text:
            return part.text
        
        return "I'm not sure how to help with that."
    
    def chat(self, message: str, conversation_history=None) -> dict:
        history_contents = []
        if conversation_history:
            for msg in conversation_history:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                if role == 'system':
                    continue
                if role == 'assistant':
                    role = 'model'
                if content:
                    history_contents.append(
                        genai.protos.Content(
                            role=role,
                            parts=[genai.protos.Part(text=content)]
                        )
                    )
        
        chat = self.model.start_chat(
            enable_automatic_function_calling=False,
            history=history_contents if history_contents else None
        )
        
        response = chat.send_message(message)
        
        if response.candidates and response.candidates[0].content.parts:
            part = response.candidates[0].content.parts[0]
            
            if hasattr(part, 'function_call') and part.function_call:
                func_call = part.function_call
                function_name = func_call.name
                function_args = dict(func_call.args)
                
                result = self._call_tool(function_name, function_args)
                
                follow_up = chat.send_message(
                    genai.protos.Content(
                        role="user",
                        parts=[genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=function_name,
                                response={"result": result}
                            )
                        )]
                    )
                )
                
                return {
                    'text': self._safe_extract_text(follow_up),
                    'tokens_used': 0
                }
            
            return {
                'text': self._safe_extract_text(response),
                'tokens_used': 0
            }
        
        return {
            'text': "I'm not sure how to help with that.",
            'tokens_used': 0
        }
    
    def process_voice(self, audio_file_path: str, conversation_history=None) -> dict:
        # Step 1: Transcribe locally using Whisper
        try:
            model = get_whisper_model()
            segments, info = model.transcribe(audio_file_path)
            user_text = " ".join([segment.text for segment in segments]).strip()
        except Exception as e:
            return {
                'user_text': '',
                'ai_text': f"Sorry, I couldn't understand the audio. Error: {str(e)}",
                'audio_url': ''
            }
        
        # Step 2: Get AI response with tools
        ai_response = self.chat(user_text, conversation_history)
        
        # Step 3: Convert to speech using gTTS
        from gtts import gTTS
        
        tts = gTTS(text=ai_response['text'], lang='en')
        
        audio_filename = f"voice_{uuid.uuid4().hex}.mp3"
        media_root = getattr(settings, 'MEDIA_ROOT', os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media'))
        audio_path = os.path.join(media_root, 'ai_agent', 'audio', audio_filename)
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        tts.save(audio_path)
        
        media_url = getattr(settings, 'MEDIA_URL', '/media/')
        if not media_url.endswith('/'):
            media_url += '/'
        
        return {
            'user_text': user_text,
            'ai_text': ai_response['text'],
            'audio_url': f"{media_url}ai_agent/audio/{audio_filename}"
        }


# Singleton
agent = GeminiAgent()