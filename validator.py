import jsonschema
import logging
from config import VOTER_SCHEMA

logger = logging.getLogger(__name__)

class Validator:
    @staticmethod
    def validate_batch(data: list) -> list:
        """
        Validates a list of voter records against the schema.
        Drops invalid records but logs them.
        """
        valid_records = []
        for index, record in enumerate(data):
            try:
                jsonschema.validate(instance=record, schema=VOTER_SCHEMA)
                valid_records.append(record)
            except jsonschema.ValidationError as e:
                logger.warning(f"Validation failed for record index {index}: {e.message}")
                # Optional: Add logic here to salvage partial data if needed
                continue
                
        return valid_records