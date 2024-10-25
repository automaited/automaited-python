
import asyncio
from io import BytesIO
import json
import logging
from pathlib import Path
import httpx
from pydantic import BaseModel
from typing import TypeVar, Type
from pydantic import BaseModel

logger = logging.getLogger("automaited")
logger.addHandler(logging.NullHandler()) 

T = TypeVar('T', bound=BaseModel)

class AsyncDocExtClient:
    def __init__(self, API_KEY: str, base_url: str = "https://docextract.mainbackend.com/api/external_devs"):
        """
        Initialize the document extraction client.
        
        :param API_KEY: API key for authenticating with the document extraction service.
        :param base_url: Base URL of the extraction API service.
        """
        self.API_KEY = API_KEY
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.API_KEY}",
            "Content-Type": "application/json"
        }
        self.logger = logging.getLogger("docext")
        self.logger.setLevel(logging.INFO)

        
    def _is_default_email(self) -> bool:
        """
        Check if the API key is the default one.
        """
        return self.API_KEY == "TEST_BETA:you@company.com"


    async def extract_model(self, model: Type[T], file_path: str | Path) -> T | None:
        """
        Extracts data from a document and maps it to a model asynchronously.
        
        :param model: The Pydantic model class to map the data to.
        :param file_path: The path to the document to be processed.
        :return: An instance of the model class populated with extracted data.
        """
        if self._is_default_email():
            self.logger.error("Please replace the placeholder email address in the API_KEY with your actual email address.\n"
                            "You will receive an email with a verification link. Re-run the script afterwards.")
            return None

        if isinstance(file_path, str):
            file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Get the model's schema
        model_schema = model.model_json_schema()

        try:
            async with httpx.AsyncClient() as client:
                # Update headers for multipart/form-data
                headers = self.headers.copy()
                headers.pop('Content-Type', None)  # Remove Content-Type as it will be set automatically

                # Submit the job
                files = {
                    'pdf_file': (file_path.name, file_path.open('rb'), 'application/pdf')
                }
                form_data = {
                    'model_schema': json.dumps(model_schema)
                }

                try:
                    submit_response = await client.post(
                        f"{self.base_url}/extract_model/submit",
                        headers=headers,
                        files=files,
                        data=form_data
                    )

                    if submit_response.status_code != 200:
                        self.logger.error(submit_response.json().get('detail'))
                        return None

                    job_id = submit_response.json()['job_id']
                finally:
                    # Ensure the file is closed after submission
                    files['pdf_file'][1].close()

                # Poll for results
                max_attempts = 60  # Maximum number of attempts (5 minutes with 5-second intervals)
                attempt = 0
                
                while attempt < max_attempts:
                    status_response = await client.get(
                        f"{self.base_url}/extract_model/status/{job_id}",
                        headers=headers
                    )

                    if status_response.status_code == 200:
                        # Job completed successfully
                        result_data = status_response.json()
                        if result_data['status'] == 'completed':
                            return model.model_validate(result_data['result'])
                        else:  # status is 'failed'
                            self.logger.error(f"Extraction failed: {result_data.get('error')}")
                            return None
                            
                    elif status_response.status_code == 202:
                        # Job still processing
                        await asyncio.sleep(1)  # Wait 5 seconds before next attempt
                        attempt += 1
                    else:
                        # Unexpected status code
                        self.logger.error(f"Unexpected response: {status_response.json().get('detail')}")
                        return None

                # If we've reached here, we've exceeded maximum attempts
                self.logger.error("Extraction timed out after 5 minutes")
                return None

        except Exception as e:
            raise Exception(f"Extraction failed: {e}")
        
class DocExtClient:
    def __init__(self, API_KEY: str, base_url: str = "https://docextract.mainbackend.com/api/external_devs"):
        """
        Initialize the document extraction client.
        
        :param API_KEY: API key for authenticating with the document extraction service.
        :param base_url: Base URL of the extraction API service.
        """
        self.async_client = AsyncDocExtClient(API_KEY, base_url)

    
    def extract_model(self, model: Type[T], file_path: str | Path) -> T:
        """
        Extracts data from a document and maps it to a model.
        
        :param model: The Pydantic model class to map the data to.
        :param file_path: The path to the document to be processed.
        :return: An instance of the model class populated with extracted data.
        """
        return asyncio.run(self.async_client.extract_model(model, file_path))