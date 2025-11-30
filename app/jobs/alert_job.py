from app.cache import cache
import logging

logger = logging.getLogger(__name__)

def process_alerts():
    try:
        pubsub = cache.client.pubsub()
        pubsub.subscribe("alerts")
        
        message = pubsub.get_message()
        if message and message['type'] == 'message':
            logger.info(f"Alert received: {message['data']}")
            
    except Exception as e:
        logger.error(f"Alert processing error: {e}")