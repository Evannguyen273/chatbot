"""
Production-safe logging utilities
"""
import logging as std_logging
from config.environment import detect_environment

class ProductionLogger:
    """Logger that handles Unicode symbols safely"""
    
    def __init__(self, name: str):
        self.logger = std_logging.getLogger(name)
        self.use_unicode = not detect_environment()
        
        # Configure logging format
        if detect_environment():
            # Production: ASCII-only format
            format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        else:
            # Development: Can use Unicode
            format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # Set up handler if not already configured
        if not self.logger.handlers:
            handler = std_logging.StreamHandler()
            formatter = std_logging.Formatter(format_str)
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(std_logging.INFO)
    
    def _format_message(self, msg: str, symbol: str = '') -> str:
        """Format message with appropriate symbol"""
        if self.use_unicode and symbol:
            return f"{symbol} {msg}"
        elif symbol:
            # Convert Unicode to ASCII
            ascii_map = {
                '🚀': '[INIT]',
                '✅': '[OK]',
                '❌': '[ERROR]',
                '🤖': '[BOT]',
                '🤔': '[PROCESSING]',
                '⚠️': '[WARNING]',
                'ℹ️': '[INFO]'
            }
            ascii_symbol = ascii_map.get(symbol, '[INFO]')
            return f"{ascii_symbol} {msg}"
        return msg
    
    def info(self, msg: str, symbol: str = 'ℹ️'):
        """Log info message with optional symbol"""
        formatted_msg = self._format_message(msg, symbol)
        self.logger.info(formatted_msg)
    
    def error(self, msg: str, symbol: str = '❌'):
        """Log error message with optional symbol"""
        formatted_msg = self._format_message(msg, symbol)
        self.logger.error(formatted_msg)
    
    def warning(self, msg: str, symbol: str = '⚠️'):
        """Log warning message with optional symbol"""
        formatted_msg = self._format_message(msg, symbol)
        self.logger.warning(formatted_msg)
    
    def success(self, msg: str, symbol: str = '✅'):
        """Log success message with optional symbol"""
        formatted_msg = self._format_message(msg, symbol)
        self.logger.info(formatted_msg)

# Global logger instance
logger = ProductionLogger('hm_assistant')