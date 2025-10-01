# Configuration for Travel Chatbot
import os
from django.core.exceptions import ImproperlyConfigured

def get_env_value(env_variable):
    """Get environment variable or raise exception"""
    try:
        return os.environ[env_variable]
    except KeyError:
        error_msg = f'Set the {env_variable} environment variable'
        raise ImproperlyConfigured(error_msg)

# Required environment variables
REQUIRED_ENV_VARS = [
    'OPENAI_API_KEY',
]

# Optional environment variables with defaults
OPTIONAL_ENV_VARS = {
    'DEBUG': 'True',
    'ALLOWED_HOSTS': 'localhost,127.0.0.1',
    'DATABASE_URL': '',
    'REDIS_URL': '',
    'SECRET_KEY': 'your-secret-key-here-change-in-production',
}

def validate_environment():
    """Validate that all required environment variables are set"""
    missing_vars = []
    
    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file or environment.")
        return False
    
    print("✅ All required environment variables are set.")
    return True

def get_database_config():
    """Get database configuration"""
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # Parse database URL (for production)
        import dj_database_url
        return dj_database_url.parse(database_url)
    else:
        # Default SQLite configuration
        return {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db.sqlite3'),
        }

def get_cache_config():
    """Get cache configuration"""
    redis_url = os.getenv('REDIS_URL')
    
    if redis_url:
        return {
            'default': {
                'BACKEND': 'django_redis.cache.RedisCache',
                'LOCATION': redis_url,
                'OPTIONS': {
                    'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                }
            }
        }
    else:
        # Default in-memory cache
        return {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'unique-snowflake',
            }
        }

# Performance settings
PERFORMANCE_SETTINGS = {
    'CHAT_RATE_LIMIT': int(os.getenv('CHAT_RATE_LIMIT', '10')),  # requests per minute
    'CACHE_TIMEOUT': int(os.getenv('CACHE_TIMEOUT', '3600')),    # 1 hour default
    'MAX_MESSAGE_LENGTH': int(os.getenv('MAX_MESSAGE_LENGTH', '1000')),
    'MAX_CHAT_HISTORY': int(os.getenv('MAX_CHAT_HISTORY', '100')),
}

# AI settings
AI_SETTINGS = {
    'OPENAI_MODEL': os.getenv('OPENAI_MODEL', 'gpt-4o'),
    'MAX_TOKENS': int(os.getenv('MAX_TOKENS', '800')),
    'TEMPERATURE': float(os.getenv('TEMPERATURE', '0.7')),
    'TIMEOUT': int(os.getenv('AI_TIMEOUT', '30')),
}

if __name__ == '__main__':
    print("🔧 Travel Chatbot Configuration Check")
    print("=" * 40)
    validate_environment()
    print(f"📊 Performance Settings: {PERFORMANCE_SETTINGS}")
    print(f"🤖 AI Settings: {AI_SETTINGS}")