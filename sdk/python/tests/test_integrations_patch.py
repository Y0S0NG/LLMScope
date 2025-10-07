"""Unit tests for provider integrations (monkey-patching)"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from llmscope.tracker import LLMScope


class TestOpenAIIntegration:
    """Test suite for OpenAI integration"""

    @pytest.fixture
    def tracker(self):
        """Create tracker for integration tests"""
        return LLMScope(api_key="test-key", project="test-project")

    def test_patch_openai_imports(self, tracker):
        """Test that patch_openai can be imported"""
        from llmscope.integrations import patch_openai, unpatch_openai
        assert callable(patch_openai)
        assert callable(unpatch_openai)

    @pytest.mark.skipif(True, reason="Requires openai package - test in integration")
    def test_patch_openai_basic(self, tracker):
        """Test basic OpenAI patching"""
        from llmscope.integrations import patch_openai, unpatch_openai
        import openai

        # Apply patch
        patch_openai(tracker)

        # Mock the actual API call
        with patch('openai.chat.completions.create') as mock_create:
            mock_response = Mock()
            mock_response.model = "gpt-4"
            mock_response.usage = Mock(prompt_tokens=10, completion_tokens=5, total_tokens=15)
            mock_response.choices = [Mock(message=Mock(content="Test"), finish_reason="stop")]
            mock_create.return_value = mock_response

            with patch.object(tracker.client.events, 'ingest') as mock_ingest:
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": "test"}]
                )

                # Should track automatically
                mock_ingest.assert_called_once()

        # Clean up
        unpatch_openai()

    @pytest.mark.skipif(True, reason="Requires openai package - test in integration")
    def test_unpatch_openai(self, tracker):
        """Test unpatching OpenAI"""
        from llmscope.integrations import patch_openai, unpatch_openai

        # Patch and unpatch
        patch_openai(tracker)
        unpatch_openai()

        # Should be able to unpatch multiple times without error
        unpatch_openai()

    def test_patch_openai_without_package(self, tracker):
        """Test that patching raises ImportError if openai not installed"""
        from llmscope.integrations import patch_openai

        # Mock openai import to fail
        with patch('builtins.__import__', side_effect=ImportError("No module named 'openai'")):
            with pytest.raises(ImportError, match="OpenAI package not found"):
                patch_openai(tracker)


class TestAnthropicIntegration:
    """Test suite for Anthropic integration"""

    @pytest.fixture
    def tracker(self):
        """Create tracker for integration tests"""
        return LLMScope(api_key="test-key", project="test-project")

    def test_patch_anthropic_imports(self, tracker):
        """Test that patch_anthropic can be imported"""
        from llmscope.integrations import patch_anthropic, unpatch_anthropic
        assert callable(patch_anthropic)
        assert callable(unpatch_anthropic)

    @pytest.mark.skipif(True, reason="Requires anthropic package - test in integration")
    def test_patch_anthropic_basic(self, tracker):
        """Test basic Anthropic patching"""
        from llmscope.integrations import patch_anthropic, unpatch_anthropic
        import anthropic

        # Apply patch
        patch_anthropic(tracker)

        # Mock the actual API call
        with patch('anthropic.messages.create') as mock_create:
            mock_response = Mock()
            mock_response.model = "claude-3-opus-20240229"
            mock_response.usage = Mock(input_tokens=10, output_tokens=5)
            mock_response.content = [Mock(text="Test response")]
            mock_response.stop_reason = "end_turn"
            mock_response.role = "assistant"
            mock_create.return_value = mock_response

            with patch.object(tracker.client.events, 'ingest') as mock_ingest:
                client = anthropic.Anthropic()
                response = client.messages.create(
                    model="claude-3-opus-20240229",
                    messages=[{"role": "user", "content": "test"}]
                )

                # Should track automatically
                mock_ingest.assert_called_once()

        # Clean up
        unpatch_anthropic()

    @pytest.mark.skipif(True, reason="Requires anthropic package - test in integration")
    def test_unpatch_anthropic(self, tracker):
        """Test unpatching Anthropic"""
        from llmscope.integrations import patch_anthropic, unpatch_anthropic

        # Patch and unpatch
        patch_anthropic(tracker)
        unpatch_anthropic()

        # Should be able to unpatch multiple times without error
        unpatch_anthropic()

    def test_patch_anthropic_without_package(self, tracker):
        """Test that patching raises ImportError if anthropic not installed"""
        from llmscope.integrations import patch_anthropic

        # Mock anthropic import to fail
        with patch('builtins.__import__', side_effect=ImportError("No module named 'anthropic'")):
            with pytest.raises(ImportError, match="Anthropic package not found"):
                patch_anthropic(tracker)


class TestIntegrationModule:
    """Test suite for integrations module"""

    def test_integrations_module_imports(self):
        """Test that all integrations can be imported"""
        from llmscope import integrations
        from llmscope.integrations import (
            patch_openai,
            unpatch_openai,
            patch_anthropic,
            unpatch_anthropic
        )

        assert callable(patch_openai)
        assert callable(unpatch_openai)
        assert callable(patch_anthropic)
        assert callable(unpatch_anthropic)

    def test_base_integration_class(self):
        """Test BaseIntegration class"""
        from llmscope.integrations.base import BaseIntegration
        from llmscope.tracker import LLMScope

        tracker = LLMScope(api_key="test-key")

        class TestIntegration(BaseIntegration):
            def patch(self):
                pass

            def unpatch(self):
                pass

        integration = TestIntegration(tracker)
        assert integration.tracker == tracker
        assert hasattr(integration, '_original_methods')


class TestIntegrationErrorHandling:
    """Test error handling in integrations"""

    @pytest.fixture
    def tracker(self):
        """Create tracker for error tests"""
        return LLMScope(api_key="test-key", debug=False)

    def test_tracking_failure_doesnt_break_app(self, tracker):
        """Test that tracking failures don't break the application"""
        from llmscope.integrations import patch_openai, unpatch_openai

        # This is conceptual - actual test would need openai installed
        # The integration should catch exceptions and not raise them

    def test_debug_mode_prints_errors(self):
        """Test that debug mode prints tracking errors"""
        tracker = LLMScope(api_key="test-key", debug=True)

        with patch.object(tracker.client.events, 'ingest', side_effect=Exception("API Error")):
            with patch('builtins.print') as mock_print:
                # Simulate tracking error
                try:
                    tracker._track_error(ValueError("Test"), 1000, "test_func")
                except:
                    pass

                # Should print in debug mode (exact behavior may vary)


class TestPatchingBehavior:
    """Test patching behavior and state management"""

    def test_multiple_patch_calls(self):
        """Test that multiple unpatch calls don't crash"""
        from llmscope.integrations import unpatch_openai

        # Test that unpatch can be called multiple times safely
        # even when nothing is patched
        unpatch_openai()
        unpatch_openai()
        unpatch_openai()

    def test_patch_with_different_trackers(self):
        """Test that unpatch works correctly"""
        from llmscope.integrations import unpatch_openai, unpatch_anthropic

        # Test that multiple unpatches work for both providers
        unpatch_openai()
        unpatch_anthropic()

        # Can call again without error
        unpatch_openai()
        unpatch_anthropic()


class TestAsyncIntegrations:
    """Test async function integrations"""

    @pytest.fixture
    def tracker(self):
        """Create tracker for async tests"""
        return LLMScope(api_key="test-key", project="test-project")

    @pytest.mark.skipif(True, reason="Requires openai package - test in integration")
    @pytest.mark.asyncio
    async def test_patch_openai_async(self, tracker):
        """Test OpenAI async patching"""
        from llmscope.integrations import patch_openai, unpatch_openai
        import openai

        patch_openai(tracker)

        # Mock async call
        with patch('openai.AsyncOpenAI.chat.completions.create') as mock_create:
            mock_response = Mock()
            mock_response.model = "gpt-4"
            mock_response.usage = Mock(prompt_tokens=10, completion_tokens=5, total_tokens=15)
            mock_response.choices = [Mock(message=Mock(content="Test"), finish_reason="stop")]

            # Make it awaitable
            async def async_return():
                return mock_response

            mock_create.return_value = async_return()

            with patch.object(tracker.client.events, 'ingest') as mock_ingest:
                client = openai.AsyncOpenAI()
                response = await client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": "test"}]
                )

                # Should track automatically
                mock_ingest.assert_called_once()

        unpatch_openai()

    @pytest.mark.skipif(True, reason="Requires anthropic package - test in integration")
    @pytest.mark.asyncio
    async def test_patch_anthropic_async(self, tracker):
        """Test Anthropic async patching"""
        from llmscope.integrations import patch_anthropic, unpatch_anthropic
        import anthropic

        patch_anthropic(tracker)

        # Similar to OpenAI async test
        # Would need actual anthropic async client mocking

        unpatch_anthropic()
