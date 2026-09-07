if __name__ == "__main__":
    from services.investigation_service import InvestigationService

    service = InvestigationService()
    result = service.get_investigation(1)
    print(result)