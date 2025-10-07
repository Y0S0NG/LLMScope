"""Unit tests for metric extractors"""
import pytest
from unittest.mock import Mock
from llmscope.extractors import (
    extract_openai_metrics,
    extract_anthropic_metrics,
    extract_generic_metrics
)


class TestOpenAIExtractor:
    """Test suite for OpenAI metric extractor"""

    def test_extract_basic_chat_completion(self):
        """Test extracting metrics from basic ChatCompletion response"""
        mock_response = Mock()
        mock_response.model = "gpt-4"
        mock_response.usage = Mock(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150
        )
        mock_response.choices = [
            Mock(
                message=Mock(content="Test response"),
                finish_reason="stop"
            )
        ]

        event = extract_openai_metrics(mock_response, 1200)

        assert event is not None
        assert event['model'] == "gpt-4"
        assert event['provider'] == "openai"
        assert event['tokens_prompt'] == 100
        assert event['tokens_completion'] == 50
        assert event['tokens_total'] == 150
        assert event['latency_ms'] == 1200
        assert event['status'] == "success"
        assert event['has_error'] is False
        assert event['response'] == "Test response"
        assert event['metadata']['finish_reason'] == "stop"

    def test_extract_with_system_fingerprint(self):
        """Test extraction with system_fingerprint"""
        mock_response = Mock()
        mock_response.model = "gpt-3.5-turbo"
        mock_response.usage = Mock(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        mock_response.choices = [Mock(message=Mock(content="Hi"), finish_reason="stop")]
        mock_response.system_fingerprint = "fp_12345"

        event = extract_openai_metrics(mock_response, 500)

        assert event['metadata']['system_fingerprint'] == "fp_12345"

    def test_extract_without_response_content(self):
        """Test extraction when response has no content"""
        mock_response = Mock()
        mock_response.model = "gpt-4"
        mock_response.usage = Mock(prompt_tokens=50, completion_tokens=25, total_tokens=75)
        mock_response.choices = []

        event = extract_openai_metrics(mock_response, 800)

        assert event is not None
        assert 'response' not in event

    def test_extract_multiple_choices(self):
        """Test extraction with multiple choices (uses first)"""
        mock_response = Mock()
        mock_response.model = "gpt-4"
        mock_response.usage = Mock(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        mock_response.choices = [
            Mock(message=Mock(content="First choice"), finish_reason="stop"),
            Mock(message=Mock(content="Second choice"), finish_reason="stop")
        ]

        event = extract_openai_metrics(mock_response, 1000)

        assert event['response'] == "First choice"

    def test_extract_with_length_finish_reason(self):
        """Test extraction with length finish_reason"""
        mock_response = Mock()
        mock_response.model = "gpt-4"
        mock_response.usage = Mock(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        mock_response.choices = [
            Mock(message=Mock(content="Truncated..."), finish_reason="length")
        ]

        event = extract_openai_metrics(mock_response, 1200)

        assert event['metadata']['finish_reason'] == "length"

    def test_extract_invalid_response(self):
        """Test extraction with invalid response returns None"""
        # Missing required attributes
        mock_response = Mock(spec=[])

        event = extract_openai_metrics(mock_response, 1000)

        assert event is None

    def test_extract_with_exception(self):
        """Test extraction handles exceptions gracefully"""
        mock_response = Mock()
        mock_response.model = Mock(side_effect=Exception("Error"))

        event = extract_openai_metrics(mock_response, 1000)

        assert event is None


class TestAnthropicExtractor:
    """Test suite for Anthropic metric extractor"""

    def test_extract_basic_message(self):
        """Test extracting metrics from basic Anthropic message"""
        mock_response = Mock()
        mock_response.model = "claude-3-opus-20240229"
        mock_response.usage = Mock(
            input_tokens=100,
            output_tokens=50
        )
        mock_response.content = [
            Mock(text="This is a test response")
        ]
        mock_response.stop_reason = "end_turn"
        mock_response.role = "assistant"

        event = extract_anthropic_metrics(mock_response, 1500)

        assert event is not None
        assert event['model'] == "claude-3-opus-20240229"
        assert event['provider'] == "anthropic"
        assert event['tokens_prompt'] == 100
        assert event['tokens_completion'] == 50
        assert event['tokens_total'] == 150
        assert event['latency_ms'] == 1500
        assert event['status'] == "success"
        assert event['has_error'] is False
        assert event['response'] == "This is a test response"
        assert event['metadata']['stop_reason'] == "end_turn"
        assert event['metadata']['role'] == "assistant"

    def test_extract_multiple_content_blocks(self):
        """Test extraction with multiple content blocks"""
        mock_response = Mock()
        mock_response.model = "claude-3-sonnet-20240229"
        mock_response.usage = Mock(input_tokens=50, output_tokens=25)
        mock_response.content = [
            Mock(text="First block"),
            Mock(text="Second block"),
            Mock(text="Third block")
        ]
        mock_response.stop_reason = "end_turn"
        mock_response.role = "assistant"

        event = extract_anthropic_metrics(mock_response, 1000)

        assert event['response'] == "First block\nSecond block\nThird block"

    def test_extract_with_max_tokens_stop_reason(self):
        """Test extraction with max_tokens stop reason"""
        mock_response = Mock()
        mock_response.model = "claude-3-opus-20240229"
        mock_response.usage = Mock(input_tokens=100, output_tokens=50)
        mock_response.content = [Mock(text="Truncated")]
        mock_response.stop_reason = "max_tokens"
        mock_response.role = "assistant"

        event = extract_anthropic_metrics(mock_response, 1200)

        assert event['metadata']['stop_reason'] == "max_tokens"

    def test_extract_empty_content(self):
        """Test extraction with empty content"""
        mock_response = Mock()
        mock_response.model = "claude-3-opus-20240229"
        mock_response.usage = Mock(input_tokens=10, output_tokens=0)
        mock_response.content = []
        mock_response.stop_reason = "end_turn"
        mock_response.role = "assistant"

        event = extract_anthropic_metrics(mock_response, 500)

        assert event is not None
        assert 'response' not in event

    def test_extract_content_without_text(self):
        """Test extraction when content blocks have no text attribute"""
        mock_response = Mock()
        mock_response.model = "claude-3-opus-20240229"
        mock_response.usage = Mock(input_tokens=50, output_tokens=25)
        mock_response.content = [Mock(spec=[])]  # No text attribute
        mock_response.stop_reason = "end_turn"
        mock_response.role = "assistant"

        event = extract_anthropic_metrics(mock_response, 1000)

        assert event is not None
        assert 'response' not in event

    def test_extract_invalid_response(self):
        """Test extraction with invalid response returns None"""
        mock_response = Mock(spec=[])

        event = extract_anthropic_metrics(mock_response, 1000)

        assert event is None

    def test_extract_with_exception(self):
        """Test extraction handles exceptions gracefully"""
        mock_response = Mock()
        mock_response.model = Mock(side_effect=Exception("Error"))

        event = extract_anthropic_metrics(mock_response, 1000)

        assert event is None


class TestGenericExtractor:
    """Test suite for generic metric extractor"""

    def test_extract_basic_metrics(self):
        """Test extracting basic generic metrics"""
        event = extract_generic_metrics(
            model="custom-model",
            provider="custom-provider",
            prompt_tokens=100,
            completion_tokens=50,
            duration_ms=1200
        )

        assert event['model'] == "custom-model"
        assert event['provider'] == "custom-provider"
        assert event['tokens_prompt'] == 100
        assert event['tokens_completion'] == 50
        assert event['tokens_total'] == 150
        assert event['latency_ms'] == 1200
        assert event['status'] == "success"
        assert event['has_error'] is False

    def test_extract_with_optional_fields(self):
        """Test extraction with optional fields"""
        event = extract_generic_metrics(
            model="gpt-4",
            provider="openai",
            prompt_tokens=200,
            completion_tokens=100,
            duration_ms=2000,
            response="Test response",
            user_id="user123",
            session_id="sess456",
            temperature=0.7,
            metadata={"custom": "value"}
        )

        assert event['response'] == "Test response"
        assert event['user_id'] == "user123"
        assert event['session_id'] == "sess456"
        assert event['temperature'] == 0.7
        assert event['metadata'] == {"custom": "value"}

    def test_extract_ignores_none_values(self):
        """Test that None values are not included"""
        event = extract_generic_metrics(
            model="gpt-4",
            provider="openai",
            prompt_tokens=100,
            completion_tokens=50,
            duration_ms=1000,
            response=None,
            user_id=None,
            metadata=None
        )

        assert 'response' not in event
        assert 'user_id' not in event
        assert 'metadata' not in event

    def test_extract_zero_tokens(self):
        """Test extraction with zero tokens"""
        event = extract_generic_metrics(
            model="test-model",
            provider="test-provider",
            prompt_tokens=0,
            completion_tokens=0,
            duration_ms=100
        )

        assert event['tokens_prompt'] == 0
        assert event['tokens_completion'] == 0
        assert event['tokens_total'] == 0

    def test_extract_with_all_fields(self):
        """Test extraction with all possible fields"""
        event = extract_generic_metrics(
            model="gpt-4",
            provider="openai",
            prompt_tokens=500,
            completion_tokens=250,
            duration_ms=3000,
            tenant_id="tenant123",
            project_id="project456",
            user_id="user789",
            session_id="session000",
            endpoint="/v1/chat/completions",
            response="Full response",
            temperature=0.8,
            max_tokens=1000,
            top_p=0.9,
            cost_usd=0.05,
            time_to_first_token_ms=500,
            status="success",
            error_message=None,
            has_error=False,
            pii_detected=False,
            metadata={"key": "value"}
        )

        assert event['tenant_id'] == "tenant123"
        assert event['project_id'] == "project456"
        assert event['user_id'] == "user789"
        assert event['endpoint'] == "/v1/chat/completions"
        assert event['temperature'] == 0.8
        assert event['max_tokens'] == 1000
        assert event['cost_usd'] == 0.05
