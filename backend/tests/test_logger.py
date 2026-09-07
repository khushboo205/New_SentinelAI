if __name__ == "__main__":
    from core.logger import LoggerFactory

    logger = LoggerFactory.get_logger("VideoLoader")
    logger.info("SentinelAI Started")
    logger.warning("Testing Warning")
    logger.error("Testing Error")