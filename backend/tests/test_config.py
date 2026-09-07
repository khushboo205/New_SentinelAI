if __name__ == "__main__":
    from core.config import Config

    config = Config()
    print(config.get("project", "name"))
    print(config.get("detector", "model"))
    print(config.get("detector", "confidence"))
    print(config.get("system", "device"))