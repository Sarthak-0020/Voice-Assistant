"""
Voice Interface Module
Handles speech recognition and text-to-speech functionality.
"""

import logging
import speech_recognition as sr
import pyttsx3
import threading
from typing import Optional
import time

logger = logging.getLogger(__name__)


class VoiceInterface:
    """Handles voice input and output for the application."""
    
    def __init__(self, settings):
        """Initialize the voice interface."""
        self.settings = settings
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize text-to-speech engine
        self.tts_engine = pyttsx3.init()
        self._configure_tts()
        
        # Calibrate for ambient noise
        self._calibrate_microphone()
        
        logger.info("Voice interface initialized")
    
    def _configure_tts(self):
        """Configure text-to-speech settings."""
        try:
            # Set speech rate
            rate = self.tts_engine.getProperty('rate')
            self.tts_engine.setProperty('rate', self.settings.speech_rate)
            
            # Set volume
            volume = self.tts_engine.getProperty('volume')
            self.tts_engine.setProperty('volume', self.settings.speech_volume)
            
            # Set voice (prefer female voice for accessibility)
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Try to find a female voice
                for voice in voices:
                    if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                else:
                    # Default to first available voice
                    self.tts_engine.setProperty('voice', voices[0].id)
            
            logger.debug("TTS engine configured successfully")
            
        except Exception as e:
            logger.warning(f"Could not configure TTS engine: {e}")
    
    def _calibrate_microphone(self):
        """Calibrate microphone for ambient noise."""
        try:
            with self.microphone as source:
                logger.info("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                logger.info("Microphone calibrated")
        except Exception as e:
            logger.error(f"Failed to calibrate microphone: {e}")
    
    def listen(self, timeout: int = 5, phrase_timeout: int = 2) -> Optional[str]:
        """
        Listen for voice input and return recognized text.
        
        Args:
            timeout: Maximum time to wait for speech to start
            phrase_timeout: Maximum time to wait for speech to complete
            
        Returns:
            Recognized text or None if no speech detected
        """
        try:
            with self.microphone as source:
                logger.debug("Listening for voice input...")
                
                # Listen for audio with timeout
                try:
                    audio = self.recognizer.listen(
                        source, 
                        timeout=timeout, 
                        phrase_time_limit=phrase_timeout
                    )
                except sr.WaitTimeoutError:
                    logger.debug("No speech detected within timeout")
                    return None
                
                # Recognize speech using Google's service
                logger.debug("Processing speech...")
                text = self.recognizer.recognize_google(audio)
                logger.info(f"Recognized: '{text}'")
                return text
                
        except sr.UnknownValueError:
            logger.debug("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Error with speech recognition service: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in speech recognition: {e}")
            return None
    
    def speak(self, text: str, interrupt_previous: bool = True):
        """
        Speak the given text using text-to-speech.
        
        Args:
            text: Text to speak
            interrupt_previous: Whether to interrupt any currently playing speech
        """
        if not text:
            return
        
        logger.info(f"Speaking: '{text}'")
        
        try:
            if interrupt_previous:
                self.tts_engine.stop()
            
            # Run TTS in a separate thread to avoid blocking
            tts_thread = threading.Thread(target=self._speak_threaded, args=(text,))
            tts_thread.daemon = True
            tts_thread.start()
            
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
    
    def _speak_threaded(self, text: str):
        """Speak text in a separate thread."""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            logger.error(f"Error in threaded speech: {e}")
    
    def listen_with_confirmation(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """
        Listen for input with spoken confirmation.
        
        Args:
            prompt: What to ask the user
            max_retries: Maximum number of retry attempts
            
        Returns:
            Recognized text or None if failed after retries
        """
        for attempt in range(max_retries):
            self.speak(prompt)
            time.sleep(0.5)  # Brief pause before listening
            
            result = self.listen(timeout=10)
            
            if result:
                # Ask for confirmation
                self.speak(f"I heard '{result}'. Is that correct? Say yes or no.")
                confirmation = self.listen(timeout=5)
                
                if confirmation and any(word in confirmation.lower() for word in ['yes', 'correct', 'right']):
                    return result
                elif confirmation and any(word in confirmation.lower() for word in ['no', 'wrong', 'incorrect']):
                    self.speak("Let me try again.")
                    continue
                else:
                    self.speak("I didn't understand your confirmation. Let me try again.")
                    continue
            else:
                if attempt < max_retries - 1:
                    self.speak("I didn't hear anything. Let me try again.")
                else:
                    self.speak("I'm having trouble hearing you. Please check your microphone.")
        
        return None
    
    def stop_speaking(self):
        """Stop any current speech output."""
        try:
            self.tts_engine.stop()
            logger.debug("Speech output stopped")
        except Exception as e:
            logger.error(f"Error stopping speech: {e}")
    
    def test_audio(self):
        """Test the audio system."""
        self.speak("Audio test. If you can hear this, the voice interface is working correctly.")
        
        self.speak("Now testing microphone. Please say something.")
        result = self.listen(timeout=10)
        
        if result:
            self.speak(f"Great! I heard you say: {result}")
            return True
        else:
            self.speak("I couldn't hear anything. Please check your microphone settings.")
            return False