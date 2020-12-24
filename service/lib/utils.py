"""Mostly tools for working with the API-Gateway input and output"""

from typing import Dict, Any
import json


def webify_output(body: str, status_code: int = 200) -> Dict[str, Any]:
    """Wraps json body so it's suitable for use as a response
    from an API-Gateway endpoint"""
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(body)
    }


def parse_path_parameters(lambda_event: Dict[str, Any]) -> Dict[str, Any]:
    return lambda_event.get('queryStringParameters', {}) or {}


def parse_body_parameters(lambda_event: Dict[str, Any]) -> Dict[str, Any]:
    params = lambda_event.get('body', '{}') or {}
    return json.loads(params)
