"""File handler for processing different file types"""
import os
import base64
from pathlib import Path

class FileHandler:
    """Handle various file types and extract content for AI analysis"""
    
    @staticmethod
    def get_file_info(file_path):
        """Get basic file information"""
        if not os.path.exists(file_path):
            return None
        
        file_size = os.path.getsize(file_path)
        file_ext = Path(file_path).suffix.lower()
        file_name = os.path.basename(file_path)
        
        return {
            'name': file_name,
            'path': file_path,
            'extension': file_ext,
            'size': file_size,
            'size_mb': round(file_size / (1024 * 1024), 2)
        }
    
    @staticmethod
    def process_file(file_path):
        """Process file and return AI-ready context"""
        info = FileHandler.get_file_info(file_path)
        if not info:
            return "❌ File not found or cannot be accessed."
        
        ext = info['extension']
        
        # Text-based files
        if ext in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.csv', '.log']:
            return FileHandler._read_text_file(file_path, info)
        
        # PDF files
        elif ext == '.pdf':
            return FileHandler._read_pdf_file(file_path, info)
        
        # Image files
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']:
            return FileHandler._analyze_image(file_path, info)
        
        # Audio files
        elif ext in ['.mp3', '.wav', '.ogg', '.m4a', '.flac']:
            return FileHandler._analyze_audio(file_path, info)
        
        # Video files
        elif ext in ['.mp4', '.avi', '.mkv', '.mov', '.webm']:
            return FileHandler._analyze_video(file_path, info)
        
        # Office documents
        elif ext in ['.docx', '.xlsx', '.pptx']:
            return FileHandler._read_office_doc(file_path, info)
        
        else:
            return f"📄 **File:** {info['name']}\n**Type:** {ext}\n**Size:** {info['size_mb']} MB\n\n⚠️ This file type is not directly supported for content analysis, but I can help you with questions about it."
    
    @staticmethod
    def _read_text_file(file_path, info):
        """Read text-based files"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(50000)  # Limit to 50K chars to avoid token limits
            
            preview = content[:2000] + "..." if len(content) > 2000 else content
            
            return f"""📄 **File:** {info['name']}
**Type:** Text/Code File
**Size:** {info['size_mb']} MB

**Content Preview:**
```
{preview}
```

**Full content available for analysis** ({len(content)} characters)
"""
        except Exception as e:
            return f"❌ Error reading file: {str(e)}"
    
    @staticmethod
    def _read_pdf_file(file_path, info):
        """Read PDF files"""
        try:
            # Try using PyPDF2
            import PyPDF2
            
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                num_pages = len(pdf_reader.pages)
                
                # Extract text from first 10 pages
                text_content = ""
                for i in range(min(10, num_pages)):
                    page = pdf_reader.pages[i]
                    text_content += page.extract_text() + "\n\n"
                
                preview = text_content[:2000] + "..." if len(text_content) > 2000 else text_content
                
                return f"""📕 **PDF File:** {info['name']}
**Pages:** {num_pages}
**Size:** {info['size_mb']} MB

**Content Preview (First {min(10, num_pages)} pages):**
```
{preview}
```

**Full PDF content available for analysis**
"""
        except ImportError:
            return f"""📕 **PDF File:** {info['name']}
**Pages:** Unknown
**Size:** {info['size_mb']} MB

⚠️ PDF text extraction requires PyPDF2 library. 
Install with: `pip install PyPDF2`

I can still help answer questions about this PDF based on filename and your description.
"""
        except Exception as e:
            return f"❌ Error reading PDF: {str(e)}"
    
    @staticmethod
    def _analyze_image(file_path, info):
        """Analyze image files"""
        try:
            from PIL import Image
            
            img = Image.open(file_path)
            width, height = img.size
            mode = img.mode
            format_name = img.format
            
            # Get image description (basic metadata only - vision API would be needed for actual content)
            return f"""🖼️ **Image File:** {info['name']}
**Format:** {format_name}
**Dimensions:** {width} x {height} pixels
**Color Mode:** {mode}
**Size:** {info['size_mb']} MB

📝 **Note:** I can see the image metadata. To analyze the actual image content (objects, text, scenes), you can:
1. Describe what you see in the image
2. Ask specific questions about it
3. Upload along with your question

Example: "What colors are in this image?" or "Describe this photo"
"""
        except ImportError:
            return f"""🖼️ **Image File:** {info['name']}
**Size:** {info['size_mb']} MB

⚠️ Image analysis requires Pillow library.
Install with: `pip install Pillow`

You can still describe the image and I'll help answer questions about it.
"""
        except Exception as e:
            return f"❌ Error analyzing image: {str(e)}"
    
    @staticmethod
    def _analyze_audio(file_path, info):
        """Analyze audio files"""
        try:
            import wave
            
            if info['extension'] == '.wav':
                with wave.open(file_path, 'rb') as wav_file:
                    channels = wav_file.getnchannels()
                    sample_width = wav_file.getsampwidth()
                    framerate = wav_file.getframerate()
                    frames = wav_file.getnframes()
                    duration = frames / framerate
                    
                    return f"""🎵 **Audio File:** {info['name']}
**Format:** WAV
**Duration:** {duration:.2f} seconds ({duration/60:.2f} minutes)
**Sample Rate:** {framerate} Hz
**Channels:** {channels} ({"Stereo" if channels == 2 else "Mono"})
**Size:** {info['size_mb']} MB

📝 **Note:** I can see audio metadata. To analyze audio content:
- Describe what you hear
- For speech, provide a transcript
- Ask questions about the audio
"""
            else:
                return f"""🎵 **Audio File:** {info['name']}
**Format:** {info['extension'].upper()}
**Size:** {info['size_mb']} MB

📝 **Note:** Audio content analysis requires transcription. You can:
1. Describe what the audio contains
2. Provide a transcript
3. Ask specific questions about it
"""
        except Exception as e:
            return f"""🎵 **Audio File:** {info['name']}
**Format:** {info['extension'].upper()}
**Size:** {info['size_mb']} MB

📝 I can help answer questions about this audio file. Please describe its content or ask specific questions.
"""
    
    @staticmethod
    def _analyze_video(file_path, info):
        """Analyze video files"""
        return f"""🎬 **Video File:** {info['name']}
**Format:** {info['extension'].upper()}
**Size:** {info['size_mb']} MB

📝 **Note:** Video analysis requires specialized tools. You can:
1. Describe what happens in the video
2. Ask questions about specific scenes
3. Provide timestamps for analysis

I can help answer questions once you describe the video content!
"""
    
    @staticmethod
    def _read_office_doc(file_path, info):
        """Read Office documents"""
        try:
            if info['extension'] == '.docx':
                from docx import Document
                doc = Document(file_path)
                
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                content = "\n\n".join(paragraphs[:20])  # First 20 paragraphs
                
                preview = content[:2000] + "..." if len(content) > 2000 else content
                
                return f"""📘 **Word Document:** {info['name']}
**Type:** DOCX
**Size:** {info['size_mb']} MB

**Content Preview:**
```
{preview}
```

**Document content available for analysis**
"""
            else:
                return f"""📗 **Office Document:** {info['name']}
**Type:** {info['extension'].upper()}
**Size:** {info['size_mb']} MB

⚠️ This document type requires specific libraries (python-docx, openpyxl, python-pptx).

You can describe the content and I'll help answer questions about it.
"""
        except ImportError:
            return f"""📗 **Office Document:** {info['name']}
**Type:** {info['extension'].upper()}
**Size:** {info['size_mb']} MB

⚠️ Office document reading requires additional libraries.
- Word: `pip install python-docx`
- Excel: `pip install openpyxl`
- PowerPoint: `pip install python-pptx`

You can describe the content and I'll help answer questions about it.
"""
        except Exception as e:
            return f"❌ Error reading document: {str(e)}"
