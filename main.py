from bot import Bot
import pyrogram.utils
import sys
import logging

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

pyrogram.utils.MIN_CHANNEL_ID = -1002507596910

if __name__ == "__main__":
    try:
        bot = Bot()
        bot.run()
    except Exception as e:
        logger.error(f"Bot failed to start: {str(e)}")
        sys.exit(1)