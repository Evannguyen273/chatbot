"""
Production-safe console utilities for Azure deployment
"""
import logging
from config.environment import detect_environment

class ProductionConsole:
    """Console output that handles Unicode symbols safely for Azure deployment"""
    
    def __init__(self):
        self.use_unicode = not detect_environment()
        
        # Set up logging
        self.logger = logging.getLogger('hm_assistant')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def _get_symbol(self, unicode_symbol: str) -> str:
        """Get appropriate symbol based on environment"""
        if self.use_unicode:
            return unicode_symbol
        
        # ASCII replacements for Azure/production
        ascii_map = {
            '🚀': '[INIT]',
            '✅': '[OK]',
            '❌': '[ERROR]',
            '🤖': '[BOT]',
            '🤔': '[PROCESSING]',
            '🎯': '[APP]',
            '💬': '[USER]',
            '👋': '[BYE]',
            '🔢': '[TEST]',
            '⚠️': '[WARNING]',
            'ℹ️': '[INFO]'
        }
        return ascii_map.get(unicode_symbol, '[INFO]')
    
    def print_with_symbol(self, message: str, symbol: str = ''):
        """Print message with environment-appropriate symbol"""
        if symbol:
            safe_symbol = self._get_symbol(symbol)
            formatted_msg = f"{safe_symbol} {message}"
        else:
            formatted_msg = message
        
        print(formatted_msg)
        
        # Also log for Azure App Service logs
        if symbol in ['❌', '⚠️']:
            self.logger.error(formatted_msg)
        else:
            self.logger.info(formatted_msg)
    
    def print_init(self, message: str):
        """Print initialization message"""
        self.print_with_symbol(message, '🚀')
    
    def print_success(self, message: str):
        """Print success message"""
        self.print_with_symbol(message, '✅')
    
    def print_error(self, message: str):
        """Print error message"""
        self.print_with_symbol(message, '❌')
    
    def print_processing(self, message: str):
        """Print processing message"""
        self.print_with_symbol(message, '🤔')
    
    def print_bot(self, message: str):
        """Print bot response"""
        self.print_with_symbol(message, '🤖')

# Global console instance
console = ProductionConsole()