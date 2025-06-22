from gradio_client import Client, handle_file
import tempfile
import os
import json

class GradioMedGemmaService:
    def __init__(self):
        self.client_url = "warshanks/medgemma-4b-it"
        self.client = None
        self.connect()
    
    def connect(self):
        """Connect to the Gradio MedGemma demo"""
        try:
            self.client = Client(self.client_url)
            print("✅ Connected to live MedGemma 4B IT demo!")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to MedGemma demo: {str(e)}")
            return False
    
    async def analyze_medical_image(self, image_file, image_type="X-Ray"):
        """
        Analyze medical image using the live MedGemma demo
        """
        try:
            if not self.client:
                self.connect()
            
            # Create a temporary file for the image
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                # Read image data (handle FastAPI UploadFile)
                if hasattr(image_file, 'read'):
                    if hasattr(image_file.read, '__call__'):
                        # Check if it's a coroutine (FastAPI UploadFile)
                        try:
                            image_data = await image_file.read()
                        except TypeError:
                            # Not async, regular file
                            image_data = image_file.read()
                    else:
                        image_data = image_file.read()
                    
                    # Reset file pointer if possible
                    try:
                        if hasattr(image_file.seek, '__call__'):
                            try:
                                await image_file.seek(0)
                            except TypeError:
                                image_file.seek(0)
                    except:
                        pass
                else:
                    with open(image_file, 'rb') as f:
                        image_data = f.read()
                
                # Write to temp file
                temp_file.write(image_data)
                temp_file_path = temp_file.name
            
            try:
                # Create medical prompt based on image type
                prompt = self.create_medical_prompt(image_type)
                
                # Call the live MedGemma demo
                result = self.client.predict(
                    message={
                        "text": prompt,
                        "files": [handle_file(temp_file_path)]
                    },
                    param_2="You are a helpful medical expert AI assistant.",  # System prompt
                    param_3=2048,  # Max new tokens
                    api_name="/chat"
                )
                
                # Parse the response
                return self.parse_gradio_response(result, image_type)
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
            
        except Exception as e:
            print(f"🔧 MedGemma Gradio API Error: {str(e)}")
            return self.get_fallback_response(image_type, str(e))
    
    def create_medical_prompt(self, image_type):
        """Create appropriate medical prompt for MedGemma"""
        prompts = {
            "xray": "Please analyze this chest X-ray image. Describe the key findings, assess the cardiomediastinal silhouette, lung fields, and any abnormalities. Provide a clinical interpretation with confidence level.",
            "x-ray": "Please analyze this chest X-ray image. Describe the key findings, assess the cardiomediastinal silhouette, lung fields, and any abnormalities. Provide a clinical interpretation with confidence level.",
            "ct": "Please analyze this CT scan image. Identify anatomical structures, assess for any abnormalities, and provide a radiological interpretation with clinical significance.",
            "mri": "Please analyze this MRI image. Evaluate the signal intensities, anatomical structures, and any pathological findings. Provide a clinical assessment.",
            "skin": "Please analyze this dermatological image. Assess the lesion characteristics, morphology, color, borders, and provide a differential diagnosis with recommendations.",
            "dermatology": "Please analyze this dermatological image. Assess the lesion characteristics, morphology, color, borders, and provide a differential diagnosis with recommendations.",
            "fundus": "Please analyze this fundus/eye image. Evaluate the optic disc, macula, blood vessels, and any retinal abnormalities. Provide an ophthalmological assessment."
        }
        
        return prompts.get(image_type.lower(), prompts["x-ray"])
    
    def parse_gradio_response(self, gradio_result, image_type):
        """Parse the Gradio MedGemma response"""
        try:
            # Extract the analysis text
            analysis_text = str(gradio_result) if gradio_result else "No analysis available"
            
            # Extract findings from the response
            findings = self.extract_findings_from_text(analysis_text)
            confidence = self.calculate_confidence_from_text(analysis_text)
            priority = self.assess_priority_from_text(analysis_text)
            recommendation = self.extract_recommendation_from_text(analysis_text)
            
            return {
                "model": "MedGemma 4B IT (Live Demo)",
                "confidence": confidence,
                "findings": findings,
                "priority": priority,
                "recommendation": recommendation,
                "raw_analysis": analysis_text,
                "technical_details": {
                    "image_type": image_type,
                    "processing_method": "Gradio Live Demo",
                    "model_source": "Google DeepMind via HuggingFace Space",
                    "api_status": "success",
                    "demo_url": "https://warshanks-medgemma-4b-it.hf.space/"
                }
            }
            
        except Exception as e:
            print(f"Response parsing error: {str(e)}")
            return self.get_fallback_response(image_type, str(e))
    
    def extract_findings_from_text(self, text):
        """Extract medical findings from MedGemma text response"""
        findings = []
        
        # Split text into sentences and extract medical content
        sentences = text.replace('\n', '. ').split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 15:  # Only meaningful sentences
                # Look for medical findings
                medical_indicators = [
                    'normal', 'abnormal', 'shows', 'indicates', 'suggests',
                    'finding', 'lesion', 'mass', 'opacity', 'infiltrate',
                    'heart', 'lung', 'bone', 'tissue', 'structure'
                ]
                
                if any(indicator in sentence.lower() for indicator in medical_indicators):
                    findings.append(f"🔬 {sentence}")
        
        # If no specific findings, use first few sentences
        if not findings:
            for sentence in sentences[:3]:
                sentence = sentence.strip()
                if len(sentence) > 20:
                    findings.append(f"📋 {sentence}")
        
        return findings if findings else ["🤖 MedGemma analysis completed successfully"]
    
    def calculate_confidence_from_text(self, text):
        """Calculate confidence based on language used"""
        confidence_keywords = {
            'normal': 88, 'clear': 85, 'obvious': 90, 'definite': 92,
            'consistent': 85, 'typical': 80, 'characteristic': 87,
            'possible': 65, 'likely': 75, 'probable': 80, 'suggests': 78,
            'uncertain': 45, 'unclear': 40, 'difficult': 50
        }
        
        text_lower = text.lower()
        confidence_scores = []
        
        for keyword, score in confidence_keywords.items():
            if keyword in text_lower:
                confidence_scores.append(score)
        
        if confidence_scores:
            return round(sum(confidence_scores) / len(confidence_scores), 1)
        else:
            return 82.5  # Default confidence
    
    def assess_priority_from_text(self, text):
        """Assess medical priority from analysis"""
        text_lower = text.lower()
        
        if any(term in text_lower for term in ['emergency', 'urgent', 'critical', 'immediate', 'acute']):
            return "HIGH"
        elif any(term in text_lower for term in ['abnormal', 'concern', 'follow', 'monitor', 'lesion']):
            return "MODERATE"
        else:
            return "LOW"
    
    def extract_recommendation_from_text(self, text):
        """Extract clinical recommendation from analysis"""
        text_lower = text.lower()
        
        if 'follow' in text_lower or 'correlation' in text_lower:
            return "MedGemma recommends clinical follow-up and correlation with symptoms"
        elif 'normal' in text_lower and 'routine' in text_lower:
            return "MedGemma suggests routine clinical management"
        elif 'specialist' in text_lower or 'referral' in text_lower:
            return "MedGemma recommends specialist consultation"
        else:
            return "MedGemma suggests clinical correlation and appropriate follow-up"
    
    def get_fallback_response(self, image_type, error_msg):
        """Fallback response if Gradio API fails"""
        return {
            "model": "MedGemma 4B IT (Fallback)",
            "confidence": 75,
            "findings": [
                "⚠️ Live MedGemma demo temporarily unavailable",
                f"🔧 Error: {error_msg[:100]}...",
                "🔄 Please try again shortly"
            ],
            "priority": "MODERATE",
            "recommendation": "Live demo fallback - please retry analysis",
            "technical_details": {
                "status": "gradio_fallback",
                "image_type": image_type,
                "demo_url": "https://warshanks-medgemma-4b-it.hf.space/"
            }
        }

# Test the service
if __name__ == "__main__":
    print("🔬 Testing Gradio MedGemma Service...")
    service = GradioMedGemmaService()
    
    if service.client:
        print("✅ Ready to analyze medical images with live MedGemma!")
    else:
        print("❌ Failed to connect to live demo") 