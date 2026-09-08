class MockResponse:
    def __init__(self) -> None:
        """Mock response"""
        self.status_code: int = 200

        local_file = 'mock_data.json'
        f = open(local_file)
        text = f.read()
        f.close()

        self.text = text
