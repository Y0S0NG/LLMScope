"""Unit tests for LLMScope auto-tracking"""
import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from llmscope.tracker import LLMScope, TrackingSpan
from llmscope.llmscope_client import LLMScopeClient


class TestLLMScope:
    """Test suite for LLMScope tracker"""

    @pytest.fixture
    def tracker(self):
        """Create LLMScope tracker instance"""
        return LLMScope(
            api_key="llmscope-local-key",
            base_url="http://localhost:8000",
            project="test-project",
            debug=False
        )

    def test_initialization(self, tracker):
        """Test LLMScope initialization"""
        assert tracker.project == "test-project"
        assert tracker.debug is False
        assert isinstance(tracker.client, LLMScopeClient)

    def test_trace_decorator_sync(self, tracker):
        """Test @trace decorator with sync function"""
        mock_response = Mock()
        mock_response.model = "gpt-4"
        mock_response.usage = Mock(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        mock_response.choices = [Mock(message=Mock(content="Test response"), finish_reason="stop")]

        with patch.object(tracker.client.events, 'ingest') as mock_ingest:
            @tracker.trace()
            def test_function():
                return mock_response

            result = test_function()

            assert result == mock_response
            mock_ingest.assert_called_once()

            # Verify event data
            call_args = mock_ingest.call_args[0][0]
            assert call_args['model'] == "gpt-4"
            assert call_args['provider'] == "openai"
            assert call_args['tokens_prompt'] == 100
            assert call_args['tokens_completion'] == 50
            assert call_args['project_id'] == "test-project"
            assert call_args['metadata']['function'] == "test_function"

    def test_trace_decorator_async(self, tracker):
        """Test @trace decorator with async function"""
        mock_response = Mock()
        mock_response.model = "gpt-4"
        mock_response.usage = Mock(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        mock_response.choices = [Mock(message=Mock(content="Test"), finish_reason="stop")]

        with patch.object(tracker.client.events, 'ingest') as mock_ingest:
            @tracker.trace()
            async def async_test_function():
                return mock_response

            result = asyncio.run(async_test_function())

            assert result == mock_response
            mock_ingest.assert_called_once()

    def test_trace_decorator_custom_name(self, tracker):
        """Test @trace decorator with custom name"""
        mock_response = Mock()
        mock_response.model = "gpt-3.5-turbo"
        mock_response.usage = Mock(prompt_tokens=50, completion_tokens=25, total_tokens=75)
        mock_response.choices = [Mock(message=Mock(content="Test"), finish_reason="stop")]

        with patch.object(tracker.client.events, 'ingest') as mock_ingest:
            @tracker.trace(name="custom_operation")
            def test_function():
                return mock_response

            test_function()

            call_args = mock_ingest.call_args[0][0]
            assert call_args['metadata']['function'] == "custom_operation"

    def test_trace_decorator_error_tracking(self, tracker):
        """Test that errors are tracked"""
        with patch.object(tracker.client.events, 'ingest') as mock_ingest:
            @tracker.trace()
            def failing_function():
                raise ValueError("Test error")

            with pytest.raises(ValueError):
                failing_function()

            # Should track the error
            mock_ingest.assert_called_once()
            call_args = mock_ingest.call_args[0][0]
            assert call_args['status'] == "error"
            assert call_args['has_error'] is True
            assert "Test error" in call_args['error_message']

    def test_trace_decorator_no_tracking_on_unknown_response(self, tracker):
        """Test that non-LLM responses don't cause errors"""
        with patch.object(tracker.client.events, 'ingest') as mock_ingest:
            @tracker.trace()
            def test_function():
                return {"some": "dict"}  # Not an LLM response

            result = test_function()

            # Should not track if extraction fails
            assert result == {"some": "dict"}
            # ingest should not be called for non-LLM responses
            assert mock_ingest.call_count == 0

    def test_context_manager_basic(self, tracker):
        """Test track() context manager"""
        span = tracker.track("test_span")
        assert isinstance(span, TrackingSpan)
        assert span.tracker == tracker
        assert span.name == "test_span"

    def test_context_manager_with_metadata(self, tracker):
        """Test context manager with metadata"""
        mock_response = Mock()
        mock_response.model = "gpt-4"
        mock_response.usage = Mock(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        mock_response.choices = [Mock(message=Mock(content="Test"), finish_reason="stop")]

        with patch.object(tracker.client.events, 'ingest') as mock_ingest:
            with tracker.track("test_operation") as span:
                span.set_metadata("user_id", "user123")
                span.set_metadata("session_id", "sess456")
                span.track_response(mock_response)

            mock_ingest.assert_called_once()
            call_args = mock_ingest.call_args[0][0]
            assert call_args['metadata']['user_id'] == "user123"
            assert call_args['metadata']['session_id'] == "sess456"

    def test_context_manager_error_tracking(self, tracker):
        """Test context manager tracks errors"""
        with patch.object(tracker.client.events, 'ingest') as mock_ingest:
            with pytest.raises(ValueError):
                with tracker.track("test_span") as span:
                    raise ValueError("Context error")

            mock_ingest.assert_called_once()
            call_args = mock_ingest.call_args[0][0]
            assert call_args['status'] == "error"
            assert call_args['has_error'] is True

    def test_tracking_span_anthropic_response(self, tracker):
        """Test TrackingSpan with Anthropic response"""
        mock_response = Mock()
        mock_response.model = "claude-3-opus-20240229"
        mock_response.usage = Mock(input_tokens=100, output_tokens=50)
        mock_response.content = [Mock(text="Test response")]
        mock_response.stop_reason = "end_turn"
        mock_response.role = "assistant"

        with patch.object(tracker.client.events, 'ingest') as mock_ingest:
            with tracker.track("anthropic_call") as span:
                span.track_response(mock_response)

            mock_ingest.assert_called_once()
            call_args = mock_ingest.call_args[0][0]
            assert call_args['model'] == "claude-3-opus-20240229"
            assert call_args['provider'] == "anthropic"
            assert call_args['tokens_prompt'] == 100
            assert call_args['tokens_completion'] == 50

    def test_debug_mode(self):
        """Test debug mode prints errors"""
        tracker = LLMScope(api_key="test-key", debug=True)

        with patch.object(tracker.client.events, 'ingest', side_effect=Exception("Tracking failed")):
            with patch('builtins.print') as mock_print:
                @tracker.trace()
                def test_function():
                    mock_response = Mock()
                    mock_response.model = "gpt-4"
                    mock_response.usage = Mock(prompt_tokens=10, completion_tokens=5, total_tokens=15)
                    mock_response.choices = [Mock(message=Mock(content="Test"), finish_reason="stop")]
                    return mock_response

                test_function()

                # Should print error in debug mode
                mock_print.assert_called()

    def test_no_project_id(self):
        """Test tracker without project ID"""
        tracker = LLMScope(api_key="test-key", project=None)

        mock_response = Mock()
        mock_response.model = "gpt-4"
        mock_response.usage = Mock(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        mock_response.choices = [Mock(message=Mock(content="Test"), finish_reason="stop")]

        with patch.object(tracker.client.events, 'ingest') as mock_ingest:
            @tracker.trace()
            def test_function():
                return mock_response

            test_function()

            call_args = mock_ingest.call_args[0][0]
            assert 'project_id' not in call_args


class TestTrackingSpan:
    """Test suite for TrackingSpan"""

    @pytest.fixture
    def tracker(self):
        """Create tracker for span tests"""
        return LLMScope(api_key="test-key", project="test")

    def test_span_timing(self, tracker):
        """Test span measures time correctly"""
        import time

        with tracker.track("test") as span:
            assert span.start_time is not None
            time.sleep(0.1)

        # Span should have measured time

    def test_span_metadata_accumulation(self, tracker):
        """Test multiple metadata calls accumulate"""
        mock_response = Mock()
        mock_response.model = "gpt-4"
        mock_response.usage = Mock(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        mock_response.choices = [Mock(message=Mock(content="Test"), finish_reason="stop")]

        with patch.object(tracker.client.events, 'ingest') as mock_ingest:
            with tracker.track() as span:
                span.set_metadata("key1", "value1")
                span.set_metadata("key2", "value2")
                span.set_metadata("key3", "value3")
                span.track_response(mock_response)

            call_args = mock_ingest.call_args[0][0]
            assert call_args['metadata']['key1'] == "value1"
            assert call_args['metadata']['key2'] == "value2"
            assert call_args['metadata']['key3'] == "value3"

    def test_span_without_tracking_response(self, tracker):
        """Test span that doesn't explicitly track response"""
        with patch.object(tracker.client.events, 'ingest') as mock_ingest:
            with tracker.track() as span:
                span.set_metadata("test", "value")
                # Don't call track_response

            # Should not ingest if no response tracked and no error
            assert mock_ingest.call_count == 0

    def test_span_track_response_failure(self, tracker):
        """Test span handles tracking failure gracefully"""
        mock_response = Mock()
        mock_response.model = "gpt-4"
        mock_response.usage = Mock(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        mock_response.choices = [Mock(message=Mock(content="Test"), finish_reason="stop")]

        with patch.object(tracker.client.events, 'ingest', side_effect=Exception("API Error")):
            # Should not raise exception
            with tracker.track() as span:
                span.track_response(mock_response)
